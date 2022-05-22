let questions = 0;

class QuizQuestion extends HTMLLIElement {
  constructor(idx) {
    super();
  }

  connectedCallback() {
    const input_1 = document.createElement('input', { "type": "text" });
    input_1.setAttribute('name', questions.toString() + '-text_1');

    const student_input_placeholder = document.createElement("span");
    student_input_placeholder.textContent = " (             ) ";
    student_input_placeholder.className = "blank-space";
    
    const input_2 = document.createElement('input', { "type": "text" });
    input_2.setAttribute('name', questions.toString() + '-text_2');
    questions += 1;

    this.appendChild(input_1);
    this.appendChild(student_input_placeholder);
    this.appendChild(input_2);
    this.className = "quiz-question";
  }
}

window.customElements.define('quiz-question', QuizQuestion, {extends: 'li'});

function addQuestion(event) {
  event.preventDefault();
  const quiz_body = document.getElementById("quiz-body");

  const qq = new QuizQuestion();
  const last_child = quiz_body.children[quiz_body.children.length - 1];
  quiz_body.insertBefore(qq, last_child);
}