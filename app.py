from uuid import uuid4
from flask import Flask, g, render_template, request, redirect, url_for
import logging, sys, sqlite3

from do_email import send_quiz_link_email

DATABASE_PATH = './homework.db'

Log_Format = "%(levelname)s %(asctime)s - %(message)s"

logging.basicConfig(filename = "logfile.log",
                    filemode = "w",
                    format = Log_Format, 
                    level = logging.ERROR)

logger = logging.getLogger()

logger.error("alert alert")

app = Flask(__name__)
db = sqlite3.connect(DATABASE_PATH)
db.cursor().executescript(open('db_init.sql').read())


def get_db():
  db = getattr(g, '_database', None)
  if db is None:
    db = g._database = sqlite3.connect(DATABASE_PATH)
  return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
def index():
  logger.info("rendering index")
  return render_template("index.html")

@app.route("/teacher/quiz/<teacher_uuid>/grade", methods=["GET", "POST"])
def grade_quiz(teacher_uuid):
  if request.method == "GET":
    db = get_db()
    cursor = db.cursor()
    student_uuid, quiz_id = cursor.execute("SELECT student_uuid, id FROM quiz WHERE teacher_uuid=?", (teacher_uuid,)).fetchone()

    questions = cursor.execute("""
      SELECT 
        text_1, 
        text_2, 
        minor_index 
      FROM question 
      WHERE quiz_id=?
    """, (quiz_id,)).fetchall()
    question_hashes = [
      {'text_1': q[0], 'text_2': q[1], 'minor_index': q[2]}
      for q in questions
    ]

    answers = cursor.execute(
      """
      SELECT 
        answer.id, 
        answer.student_id, 
        answer.minor_index, 
        answer.response_1,
        feedback.score,
        student.name
      FROM answer 
      LEFT JOIN feedback
        ON feedback.answer_id = answer.id
      LEFT JOIN student
        ON answer.student_id = student.id
      WHERE quiz_id=?
      ORDER BY answer.id, feedback.id
      """,
      (quiz_id,)
    ).fetchall()

    for qh in question_hashes:
      qh['answers'] = {
        a[0]: {
          'id': a[0],
          'student_id': a[1],
          'response_1': a[3],
          'score': a[4],
          'student name': a[5],
        }
        for a in answers
        if a[2] == qh['minor_index']
      }

    print("qh", question_hashes)
    return render_template('grade.html', teacher_uuid=teacher_uuid, student_uuid=student_uuid, questions=question_hashes)

  if request.method == "POST":
    db = get_db()
    cursor = db.cursor()

    parsed_form = []

    for key, val in request.form.items():
      _, answer_id = key.split("-")
      parsed_form.append({'answer_id': answer_id, 'score': val})
    cursor.executemany("INSERT INTO feedback (answer_id, score) VALUES (:answer_id, :score)", parsed_form)
    db.commit()
    return redirect(request.url)

@app.route("/teacher/quiz/<teacher_uuid>/links")
def quiz_links(teacher_uuid):
  db = get_db()
  cursor = db.cursor()
  student_uuid = cursor.execute("SELECT student_uuid FROM quiz WHERE teacher_uuid=?", (teacher_uuid,)).fetchone()[0]
  return render_template('links.html', teacher_uuid=teacher_uuid, student_uuid=student_uuid)

@app.route("/student/quiz/<student_uuid>/take")
def take_quiz(student_uuid):
  db = get_db()
  cursor = db.cursor()
  quiz_id = cursor.execute("SELECT id FROM quiz WHERE student_uuid=?", (student_uuid,)).fetchone()[0]
  questions = cursor.execute("SELECT text_1, text_2, minor_index FROM question WHERE quiz_id=?", (quiz_id,)).fetchall()

  quiz_headers = load_quiz_headers(cursor, quiz_id)

  return render_template("take_quiz.html", student_uuid=student_uuid, questions=questions, quiz_headers=quiz_headers)

@app.route("/student/quiz/<student_uuid>/submit", methods=["POST"])
def submit_quiz(student_uuid):
  parsed_form = {}
  for input_name, text in request.form.items():
    form_section, question_id = input_name.split("-")
    parsed_form[form_section] = parsed_form.get(form_section, {})
    parsed_form[form_section][question_id] = text

  db = get_db()
  cursor = db.cursor()

  cursor.execute(
    "INSERT INTO student (name, email) VALUES (?, ?)",
    (parsed_form['header']['student_name'], parsed_form['header']['student_email']),
  )
  student_id = cursor.lastrowid

  quiz_id = cursor.execute(
    "SELECT id FROM quiz WHERE student_uuid=?", (student_uuid,)
  ).fetchone()[0]

  cursor.executemany(
    "INSERT INTO answer (student_id, quiz_id, minor_index, response_1) VALUES (?, ?, ?, ?)",
    [(student_id, quiz_id, minor_index, response) for minor_index, response in parsed_form['question'].items()]
  )
  db.commit()

  return redirect(url_for("see_feedback", student_uuid=student_uuid, student_id=student_id))

@app.route("/student/quiz/<student_uuid>/feedback/<student_id>", methods=["GET"])
def see_feedback(student_uuid, student_id):
  db = get_db()
  cursor = db.cursor()

  quiz_id = cursor.execute("SELECT id FROM quiz WHERE student_uuid=?", (student_uuid,)).fetchone()[0]


  student_metadata = cursor.execute("""
    SELECT
      student.name, 
      student.email
    FROM
      student
    WHERE
      student.id = ?
  """, (student_id,)).fetchone()
  student_metadata = {
    "student name": student_metadata[0],
    "student email": student_metadata[1]
  }

  questions = cursor.execute(
    "SELECT text_1, text_2, minor_index FROM question WHERE quiz_id=?", 
    (quiz_id,)
  ).fetchall()
  question_hashes = [
    {'text_1': q[0], 'text_2': q[1], 'minor_index': q[2]}
    for q in questions
  ]

  answers = cursor.execute(
    """
    SELECT 
      answer.minor_index, 
      answer.response_1,
      feedback.score
    FROM 
      answer 
    LEFT JOIN feedback ON feedback.answer_id = answer.id
    WHERE quiz_id=? AND student_id=?
    """, 
    (quiz_id, student_id)
  ).fetchall()
  answers_hash = {answer[0]: {'response_1': answer[1], 'score': answer[2]} for answer in answers}

  for question in question_hashes:
    question['response_1'] = answers_hash[question['minor_index']]['response_1']
    question['score'] = answers_hash[question['minor_index']]['score']

  quiz_headers = load_quiz_headers(cursor, quiz_id)

  return render_template(
    'feedback.html', 
    questions=question_hashes, 
    quiz_headers=quiz_headers,
    student_metadata=student_metadata,
  )

@app.route("/teacher/create_quiz", methods=["POST"])
def create_quiz():
  out = {}
  for input_name, text in request.form.items():
    question_number, question_part = input_name.split('-')
    out[question_number] = out.get(question_number, {})
    out[question_number][question_part] = text
  
  db = get_db()
  cursor = db.cursor()
  cursor.execute(
    "INSERT INTO teacher (name, email) VALUES (?, ?)", 
    (
      out['header']['teacher_name'], 
      out['header']['teacher_email']
    )
  )
  teacher_id = cursor.lastrowid

  student_uuid = str(uuid4())
  teacher_uuid = str(uuid4())
  cursor.execute(
    "INSERT INTO quiz (name, teacher_id, student_uuid, teacher_uuid) VALUES (?, ?, ?, ?)",
    (out['header']['quiz_name'], teacher_id, student_uuid, teacher_uuid)
  )
  quiz_id = cursor.lastrowid

  questions = [val for key, val in out.items() if key.isdigit()]
  for idx, q in enumerate(questions):
    q["idx"] = idx
  query = f"INSERT INTO question (text_1, text_2, minor_index, question_type, quiz_id) VALUES (:text_1, :text_2, :idx, 'single_blank', {quiz_id})"
  cursor.executemany(query, questions)
  db.commit()

  url = url_for('quiz_links', teacher_uuid=teacher_uuid)
  send_quiz_link_email("me@jtbooth.com", out['header']['teacher_email'], "Quiz Links", url)
  return redirect(url)

def load_quiz_headers(cursor, quiz_id):
  quiz_headers = cursor.execute("""
    SELECT 
      quiz.name as quiz_name, 
      teacher.name as teacher_name, 
      teacher.email as teacher_email  
    FROM quiz 
    INNER JOIN teacher ON quiz.teacher_id = teacher.id
    WHERE quiz.id = ?
  """, (quiz_id,)).fetchone()
  quiz_headers = {
    "quiz name": quiz_headers[0],
    "teacher name": quiz_headers[1],
    "teacher email": quiz_headers[2],
  }
  return quiz_headers 