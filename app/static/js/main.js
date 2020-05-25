var quizGrades = {};

const getSelectValue = () => {
  var e = document.getElementById("course_id_report");
  var strUser = e.options[e.selectedIndex].value;
  console.log(strUser);
  // get reference to select element
  let sel = document.getElementById('quiz_id_report');

  deleteOption();
  let firstOption = document.createElement('option');
  firstOption.appendChild(document.createTextNode('Выберете задание'));
  sel.appendChild(firstOption);

  // create new option element
  let opt = document.createElement('option');

  // create text node to add to option element (opt)
  opt.appendChild(document.createTextNode('New Option Text'));

  // set value property of opt
  opt.value = '3';

  // add opt to end of select box (sel)
  sel.appendChild(opt);
}

const deleteOption = () => {
  let selec = document.getElementById('quiz_id_report');
  while (selec.firstChild) {
    selec.removeChild(selec.lastChild);
  }
}

const deleteOptionChart = () => {
  let selec = document.getElementById('quiz_id_chart');
  while (selec.firstChild) {
    selec.removeChild(selec.lastChild);
  }
}

const createOptions = (data) => {
  let sel = document.getElementById('quiz_id_report');

  deleteOption();
  let firstOption = document.createElement('option');
  firstOption.appendChild(document.createTextNode('Выберете задание'));
  sel.appendChild(firstOption);
  quizGrades = {};

  // create new option element
  data['quizzes'].forEach(element => {
    let opt = document.createElement('option');

    // create text node to add to option element (opt)
    opt.appendChild(document.createTextNode(`${element['name']}`));

    // set value property of opt
    opt.value = `${element['id']}`;

    // add opt to end of select box (sel)
    sel.appendChild(opt);
    quizGrades[element['name']] = element['sumgrades'];
    console.log(quizGrades);
  });

}

// TODO: remove chart, union chart and table function

const createOptionsChart = (data) => {
  let sel = document.getElementById('quiz_id_chart');

  deleteOptionChart();
  let firstOption = document.createElement('option');
  firstOption.appendChild(document.createTextNode('Выберете задание'));
  sel.appendChild(firstOption);
  quizGrades = {};

  // create new option element
  data['quizzes'].forEach(element => {
    let opt = document.createElement('option');

    // create text node to add to option element (opt)
    opt.appendChild(document.createTextNode(`${element['name']}`));

    // set value property of opt
    opt.value = `${element['id']}`;

    // add opt to end of select box (sel)
    sel.appendChild(opt);
    quizGrades[element['name']] = element['sumgrades'];
    console.log(quizGrades);
  });

}

const getQuizzes = () => {
  let e = document.getElementById("course_id_report");
  let optionValue = e.options[e.selectedIndex].value;
  // console.log(optionValue);
  // 1. Создаём новый объект XMLHttpRequest
  var xhr = new XMLHttpRequest();

  // 2. Конфигурируем его: GET-запрос на URL 'phones.json'
  xhr.open('GET', `https://test-bsc.moodlecloud.com/webservice/rest/server.php?wstoken=6fc59f99230d7bb8376afa8690369b7f&wsfunction=mod_quiz_get_quizzes_by_courses&moodlewsrestformat=json&courseids[0]=${optionValue}`, false);

  // 3. Отсылаем запрос
  xhr.send();

  // 4. Если код ответа сервера не 200, то это ошибка
  if (xhr.status != 200) {
    // обработать ошибку
    alert(xhr.status + ': ' + xhr.statusText); // пример вывода: 404: Not Found
  } else {
    // вывести результат
    // console.log(JSON.parse(xhr.responseText)); // responseText -- текст ответа.
    createOptions(JSON.parse(xhr.responseText))
    return JSON.parse(xhr.responseText);
  }
}

const getQuizzesChart = () => {
  let e = document.getElementById("course_id_chart");
  let optionValue = e.options[e.selectedIndex].value;
  // console.log(optionValue);
  // 1. Создаём новый объект XMLHttpRequest
  var xhr = new XMLHttpRequest();

  // 2. Конфигурируем его: GET-запрос на URL 'phones.json'
  xhr.open('GET', `https://test-bsc.moodlecloud.com/webservice/rest/server.php?wstoken=6fc59f99230d7bb8376afa8690369b7f&wsfunction=mod_quiz_get_quizzes_by_courses&moodlewsrestformat=json&courseids[0]=${optionValue}`, false);

  // 3. Отсылаем запрос
  xhr.send();

  // 4. Если код ответа сервера не 200, то это ошибка
  if (xhr.status != 200) {
    // обработать ошибку
    alert(xhr.status + ': ' + xhr.statusText); // пример вывода: 404: Not Found
  } else {
    // вывести результат
    // console.log(JSON.parse(xhr.responseText)); // responseText -- текст ответа.
    createOptionsChart(JSON.parse(xhr.responseText))
    return JSON.parse(xhr.responseText);
  }
}

const setGrades = () => {
  let quiz = document.getElementById("quiz_id_report");
  let optionValue = quiz.options[quiz.selectedIndex].text;
  // console.log(optionValue);
  let grade = document.getElementById("sumgrades_report");
  // console.log(quizGrades[optionValue]);
  grade.value = quizGrades[optionValue];
}

const setGradesChart = () => {
  let quiz = document.getElementById("quiz_id_chart");
  let optionValue = quiz.options[quiz.selectedIndex].text;
  // console.log(optionValue);
  let grade = document.getElementById("sumgrades_chart");
  // console.log(quizGrades[optionValue]);
  grade.value = quizGrades[optionValue];
}