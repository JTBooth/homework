required_fields = {
  'header-quiz_name': false,
  'header-teacher_name': false,
  'header-teacher_email': false
};

take_quiz = {
  'header-student_name': false,
  'header-student_email': false,
};

hash_of_hashes = {
  'index': required_fields,
  'take_quiz': take_quiz
};

function trackInput(hash_name, field_name, value) {
  let hash = hash_of_hashes[hash_name];
  hash[field_name] = !!value;

  if (Object.values(hash).every(x => x === true)) {
    document.getElementById('submit-button').disabled = false;
  } else {
    document.getElementById('submit-button').disabled = true;
  }
}
