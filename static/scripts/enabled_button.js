required_fields = [
  'header-quiz_name',
  'header-teacher_name',
  'header-teacher_email'
];

take_quiz = [
  'header-student_name',
  'header-student_email',
];

hash_of_fieldsets = {
  'index': required_fields,
  'take_quiz': take_quiz
};

function trackInput(fieldset) {
  let fields = hash_of_fieldsets[fieldset];
  let disabled = false;
  fields.forEach(field_name => {
    if (!document.getElementById(field_name).value) {
      disabled = true;
    }
  })
  document.getElementById('submit-button').disabled = disabled;
}
