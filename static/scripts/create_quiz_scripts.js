let questions = 0;

class QuizQuestion extends HTMLLIElement {
  constructor() {
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

    const delete_button = document.createElement('button');
    delete_button.setAttribute("class", "delete-button");
    delete_button.onclick = () => this.remove();
    delete_button.textContent = "✖";

    this.appendChild(input_1);
    this.appendChild(student_input_placeholder);
    this.appendChild(input_2);
    this.appendChild(delete_button);
    this.className = "quiz-question";
  }
}

window.customElements.define('quiz-question', QuizQuestion, {extends: 'li'});

class ExampleQuizQuestion extends HTMLLIElement {
  constructor() {
    super();
  }

  connectedCallback() {
    const input_1 = document.createElement('input', { "type": "text" });
    input_1.value = this.getAttribute('left_text');
    input_1.setAttribute('disabled', true);

    const student_input_placeholder = document.createElement("span");
    student_input_placeholder.textContent = " (             ) ";
    student_input_placeholder.className = "blank-space";
    
    const input_2 = document.createElement('input', { "type": "text" });
    input_2.value = this.getAttribute('right_text');
    input_2.setAttribute('disabled', true);
    questions += 1;

    this.appendChild(input_1);
    this.appendChild(student_input_placeholder);
    this.appendChild(input_2);
    this.className = "example-quiz-question";
  }
}

window.customElements.define('example-quiz-question', ExampleQuizQuestion, {extends: 'li'});

function addQuestion(event) {
  event.preventDefault();
  const quiz_body = document.getElementById("quiz-body");

  const qq = new QuizQuestion();
  quiz_body.appendChild(qq);
}