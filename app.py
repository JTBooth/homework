from uuid import uuid4
from flask import Flask, g, render_template, request, redirect
import sqlite3

DATABASE_PATH = './homework.db'

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
  return render_template("index.html")

@app.route("/teacher/quiz/<teacher_uuid>/grade", methods=["GET", "POST"])
def grade_quiz(teacher_uuid):
  if request.method == "GET":
    db = get_db()
    cursor = db.cursor()
    student_uuid, quiz_id = cursor.execute("SELECT student_uuid, id FROM quiz WHERE teacher_uuid=?", (teacher_uuid,)).fetchone()
    print("student uuid, quiz id", student_uuid, quiz_id)

    questions = cursor.execute("SELECT text_1, text_2, minor_index FROM question WHERE quiz_id=?", (quiz_id,)).fetchall()
    question_hashes = [
      {'text_1': q[0], 'text_2': q[1], 'minor_index': q[2]}
      for q in questions
    ]

    answers = cursor.execute(
      "SELECT student_id, minor_index, response_1 FROM answer WHERE quiz_id=?",
      (quiz_id,)
    ).fetchall()

    for qh in question_hashes:
      qh['answers'] = [
        {
          'student_id': a[0],
          'response_1': a[2]
        }
        for a in answers
        if a[1] == qh['minor_index']
      ]

    return render_template('grade.html', teacher_uuid=teacher_uuid, student_uuid=student_uuid, questions=question_hashes)

  if request.method == "POST":
    print(request.form)
    return {}

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
  print("questions:", questions)

  return render_template("take_quiz.html", student_uuid=student_uuid, questions=questions)

@app.route("/student/quiz/<student_uuid>/submit", methods=["POST"])
def submit_quiz(student_uuid):
  print("submitted quiz")
  print(request.form)
  
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

  return redirect(f"http://localhost:5000/student/quiz/{student_uuid}/feedback/{student_id}")

@app.route("/student/quiz/<student_uuid>/feedback/<student_id>", methods=["GET"])
def see_feedback(student_uuid, student_id):
  db = get_db()
  cursor = db.cursor()

  quiz_id = cursor.execute("SELECT id FROM quiz WHERE student_uuid=?", (student_uuid,)).fetchone()[0]

  questions = cursor.execute(
    "SELECT text_1, text_2, minor_index FROM question WHERE quiz_id=?", 
    (quiz_id,)
  ).fetchall()
  question_hashes = [
    {'text_1': q[0], 'text_2': q[1], 'minor_index': q[2]}
    for q in questions
  ]

  answers = cursor.execute(
    "SELECT minor_index, response_1 FROM answer WHERE quiz_id=? AND student_id=?", 
    (quiz_id, student_id)
  ).fetchall()

  answers_hash = {answer[0]: answer[1] for answer in answers}
  for question in question_hashes:
    question['response_1'] = answers_hash[question['minor_index']]

  return render_template('feedback.html', questions=question_hashes)

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
  print("query:", query)
  cursor.executemany(query, questions)
  db.commit()

  return redirect(f"http://localhost:5000/teacher/quiz/{teacher_uuid}/links")
