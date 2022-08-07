required_fields = {
  'header-quiz_name': false,
  'header-teacher_name': false,
  'header-teacher_email': false,
};

take_quiz = {
  'header-student_name': false,
  'header-student_email': false,
};

hash_of_fieldsets = {
  'index': required_fields,
  'take_quiz': take_quiz
};

function notEmptyValidator(text) {
  return (typeof text === 'string') && (text.length > 0);
}

function emailValidator(email) {
  return email.match(
    /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
  );
};

function trackInput(fieldset, field_name, target_value, validation) {
  let fields = hash_of_fieldsets[fieldset];
  if (validation(target_value)) {
    fields[field_name] = true;
  } else {
    fields[field_name] = false;
  }

  console.log(fields);
  if (Object.values(fields).every(x => x === true)) {
    document.getElementById('submit-button').disabled = false;
  } else {
    document.getElementById('submit-button').disabled = true;
  }
}
