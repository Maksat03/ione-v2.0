let test_is_final_test = false;
var test_was_passed = false;

function retake() {
  window.location.hash = null;
  window.location.reload();
}

const sendData = () => {
  if (test_was_passed) {
    retake();
  }
  else {
    var formData = {
      csrfmiddlewaretoken: $('.check_test_form input[name="csrfmiddlewaretoken"]').val(),
    };
    var questions = document.getElementsByClassName("question");
  
    for (var i = questions.length - 1; i >= 0; i--) {
      question_id = questions[i].getAttribute("data-question-id");
      formData[question_id] = [];
      var choices = document.getElementsByClassName("choice"+question_id);
      for (var j = choices.length - 1; j >= 0; j--) {
        if (choices[j].checked) {
          formData[question_id].push(choices[j].getAttribute("data-choice-id"));
        }
      }
    }
  
    $.ajax({
      type: "POST",
      url: "test/check/",
      data: JSON.stringify(formData),
      dataType: "json",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": $.cookie("csrftoken"),
      },
      success: (response) => {  
        var number_of_correct_answers = 0;

        var keys = Object.keys(response);
        for (var i = 0; i < questions.length; i++) {
          var question_id = questions[i].getAttribute("data-question-id");
          if (keys.includes(question_id)) {
            var answer_is_correct = response[question_id];
            var text = questions[i].innerText;
            if (answer_is_correct) {
              number_of_correct_answers += 1;
              text += " <span style='color: green;'>Правильный ответ</span>"
            }
            else {
              var choices = document.getElementsByClassName("choice"+question_id);
              var has_not_choices = true;
              for (var j = choices.length - 1; j >= 0; j--) {
                if (choices[j].checked) {
                  text += " <span style='color: red;'>Неправильный ответ</span>"
                  has_not_choices = false;
                  break;
                }
              }
              if (has_not_choices) {
                text += " <span style='color: red;'>Нет ответа</span>"
              }
            }
            questions[i].innerHTML = text;
          }
        }
        
        var res = document.getElementsByClassName("lessontest_results")[0];
        res.innerHTML = "Результат: " + Number((response["total"]).toFixed(1)) + "%<br>" + number_of_correct_answers + " / " + questions.length + " правильних ответов";
        res.style.display = "block";
        
        if (Number((response["total"]).toFixed(1)) > 70) {
          if (response["final_test_was_opened"]) {
            var splitted_url = window.location.href.split("/");
            splitted_url.splice(splitted_url.length - 1);
            splitted_url.splice(splitted_url.length - 1);
            splitted_url.splice(splitted_url.length - 1);
            splitted_url.push("final_test");
            var final_test_url = splitted_url.join("/");
            res.innerHTML += "<h3>Вы прошли тест и прошли весь курс, теперь вам открыто <a href='"+ final_test_url +"'>Финальный экзамен.</a> После пройдение финального теста, вы полностью завершите курс</h3>"
            Swal.fire({
              title: "<i>Поздравляем</i>", 
              html: "Вам прошил весь курс и вам теперь доступен <a href='"+ final_test_url +"'>финальный экзамен</a>, после прохождение финального экзамена в полностью закончите курс.",  
              confirmButtonText: "<u>Окей</u>", 
            });
          }
          else if (response["course_was_completed"]) {
            res.innerHTML += "\n<h3>Вы прошли весь курс.</h3>"
            if (response["course_has_certificate"]) {
              res.innerHTML += "Вы можете получить сертификат этого курса передя в профиль"
              Swal.fire({
                title: "<i>Поздравляем</i>", 
                html: "Вы прошли весь курс. Вы можете получить сертификат этого курса передя в профиль",  
                confirmButtonText: "<u><a style='color: white; text-decoration: none;' target='_blank' href='"+ response["certificate_url"] +"'>Получить сертификат</a></u>", 
              });
            }
            else {
              Swal.fire({
                title: "<i>Поздравляем</i>", 
                html: "Вы прошли весь курс.",  
                confirmButtonText: "<u>Окей</u>", 
              });
            }
          }
          else {
            res.innerHTML += "<h3>Вы прошли тест</h3>"
          }
        }
        else {
          res.innerHTML += `<h3>Вы не смогли сдать тест ${Number((response["total"]).toFixed(1))}% < 70%`
        }

        var lessontest_check_button = document.getElementsByClassName("lessontest_check_button")[0];
        lessontest_check_button.innerText = "Пересдать";
        test_was_passed = true;

        if (test_is_final_test) {
          final_test_was_submitted = true;
        }

      },
      error: (error) => {
        console.log(error);
      }
    })
  }
}

$(".check_test_form").submit(function (event) {
  event.preventDefault();
  sendData();
});