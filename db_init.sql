-- Holds the email the teacher_uuid link is sent to
CREATE TABLE IF NOT EXISTS teacher (
  id INTEGER PRIMARY KEY,
  name TEXT,
  email TEXT
);

-- Holds the IDs used to access different portions of a quiz
CREATE TABLE IF NOT EXISTS quiz (
  id INTEGER PRIMARY KEY,
  name TEXT,
  teacher_id INTEGER NOT NULL,
  student_uuid TEXT NOT NULL,
  teacher_uuid TEXT NOT NULL,
  
  FOREIGN KEY (teacher_id) REFERENCES teacher (id)
);

-- List questions associated to quizzes.
CREATE TABLE IF NOT EXISTS question (
  id INTEGER PRIMARY KEY,
  text_1 TEXT,
  text_2 TEXT,
  minor_index INTEGER,
  question_type TEXT,
  quiz_id INTEGER 
);

CREATE TABLE IF NOT EXISTS student (
  id INTEGER PRIMARY KEY,
  name TEXT,
  email TEXT
);

CREATE TABLE IF NOT EXISTS answer (
  id INTEGER PRIMARY KEY,
  student_id INTEGER,
  quiz_id INTEGER,
  minor_index INTEGER,
  response_1 TEXT,

  FOREIGN KEY (student_id) REFERENCES student (id),
  FOREIGN KEY (quiz_id)    REFERENCES quiz    (id)
);

CREATE TABLE IF NOT EXISTS feedback (
  id INTEGER PRIMARY KEY,
  answer_id INTEGER,
  score TEXT,

  FOREIGN KEY (answer_id) REFERENCES answer (id)
);
