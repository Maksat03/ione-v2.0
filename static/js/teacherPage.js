var pages = ["docs", "proceeds", "courses", "feedback_list"]

function func(el) {
    var id = el.getAttribute("data-id")
    for (var i = pages.length - 1; i >= 0; i--) {
        var element = document.getElementById(pages[i])
        var btn = document.getElementById("btn-"+pages[i])
        if (pages[i] != id) {
            element.style.display = "none"
            btn.value = 0
        } else {
            if (pages[i] == "feedback_list") {
                element.style.display = "flex"
            } else {
                element.style.display = "block"
            }
            btn.value = 1
        }
    }
}

function show_call_center_with_sweet_alert() {
    Swal.fire({
      title: "<i>Наш кол центр</i>",
      html: "ione.team.kz@gmail.com<br>+7 (708) 115 64-54",
      confirmButtonText: "<u>Окей</u>",
    });
}

function erase_change_password_form_errors() {
  var fields = ["old_password", "new_password1", "new_password2"]
  fields.forEach((field) => {
    var field_errors = document.getElementById(field + '_field_errors');
    field_errors.innerHTML = "";
  })
}

function show_change_password_form_errors(errors) {
  erase_change_password_form_errors();
  Object.keys(errors).forEach((key) => {
    var field_errors = document.getElementById(key + '_field_errors');
    var txt = "<ul>";

    for (var i = errors[key].length - 1; i >= 0; i--) {
      txt += "<li>" + errors[key][i] + "</li>";
    }

    field_errors.innerHTML = txt + "</ul>";
  })
}

$(".change_password_form").submit(function (event) {
  var formData = new FormData();
  formData.append('csrfmiddlewaretoken', $('.change_password_form input[name="csrfmiddlewaretoken"]').val());
  formData.append("old_password", $("#id_old_password").val());
  formData.append("new_password1", $("#id_new_password1").val());
  formData.append("new_password2", $("#id_new_password2").val());

  $.ajax({
    type: "POST",
    url: "change-password/",
    data: formData,
    dataType: "json",
    processData: false,
    contentType: false,
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": $.cookie("csrftoken"),
    },
    success: (response) => {
      if (response["success"]) {
        document.getElementsByClassName("change-password-form-container")[0].innerText = "Пароль успешно изменен";
        document.getElementsByClassName("last_password_changing")[0].innerText = "Пароль только что был изменен";
      }
      else {
        show_change_password_form_errors(response["errors"]);
      }
    },
    error: (error) => {
      console.log(error);
    }
  })

  event.preventDefault();
});

function open_lessons_of_course(course_id) {
  var lessons = document.getElementsByClassName("teacher_lessons_name");
  for (var i = lessons.length - 1; i >= 0; i--) {
    if (lessons[i].id == "lessons_of_course_" + course_id) {
      lessons[i].style.display = "block"
    } else {
      lessons[i].style.display = "none"
    }
  }
  var forums = document.getElementsByClassName("teacher_courses_coms");
  for (var i = forums.length - 1; i >= 0; i--) {
    forums[i].style.display = "none"
    forums[i].getElementsByClassName("courses_com")[0].innerHTML = ""
  }
}
let current_lesson_id = 0;
function open_forum_of_lesson(lesson_id) {
  var forums = document.getElementsByClassName("teacher_courses_coms");
  for (var i = forums.length - 1; i >= 0; i--) {
    forums[i].getElementsByClassName("courses_com")[0].innerHTML = ""
    if (forums[i].id == "forum_of_lesson_" + lesson_id) {
      forums[i].style.display = "block"
      load_messages_of_forum(lesson_id, 0, 20)
    } else {
      forums[i].style.display = "none"
      current_lesson_id = parseInt(forums[i].id.replace("forum_of_lesson_", ""))
      cancel_answer_form()
    }
  }
  current_lesson_id = lesson_id
}

function load_messages_of_forum(lesson_id, startswith, endswith) {
  console.log(this)
  $.ajax({
    url: `load_messages_of_forum/?lesson_id=${lesson_id}&startswith=${startswith}&endswith=${endswith}`,
    success: (response) => {
      console.log(response)
      show_messages(lesson_id, response["messages"], response["no_more_messages"], response["startswith"], response["endswith"])
    },
    error: (err) => {
      console.log(err)
    }
  })
}

function load_nested_messages_of_forum(parent_message_id, startswith, endswith) {
  console.log(this)
  $.ajax({
    url: `load_nested_messages_of_forum/?parent_message_id=${parent_message_id}&startswith=${startswith}&endswith=${endswith}`,
    success: (response) => {
      console.log(response)
      show_nested_messages(parent_message_id, response["messages"], response["no_more_nested_messages"], response["startswith"], response["endswith"])
    },
    error: (err) => {
      console.log(err)
    }
  })
}


function show_messages(lesson_id, messages, no_more_messages, startswith, endswith) {
  var messages_block = document.getElementById("forum_of_lesson_" + lesson_id).getElementsByClassName("courses_com")[0]
  for (var i = 0; i < messages.length; i++) {
    messages_block.innerHTML += `
      <div class="com_text" id="message_${messages[i]["pk"]}_0">
        <div class="usersCom" style="margin-top: 0">
          <div class="userImg">
            <button style="background-image: url(${messages[i]["fields"]["user_img"]})" type="button" class="image_btn"></button>
          </div>
          <div class="user">
            <p style="color: #4E9F3D; font-weight: bold; margin: 0" class="username">${messages[i]["fields"]["user"]}</p>

            <div class="rating">
              <span>${messages[i]["fields"]["date"]}</span>
            </div>

            <p style="margin: 10px 0">${messages[i]["fields"]["comment"]} <a onclick="set_answer_form(${messages[i]["pk"]})">Ответить</a></p>
            <hr>
            <div class="comAnswer" id="parent_message_${messages[i]["pk"]}"></div>
          </div>
        </div>
      </div>
    `
    if (i != 0) {
      messages_block.innerHTML += `<hr>`
    }
    show_nested_messages(messages[i]["pk"], messages[i]["nested_comments"], messages[i]["no_more_nested_messages"], 5, 10)
  }
  if (!no_more_messages) {
    messages_block.innerHTML += `
      <button onclick="this.style.display = 'none'; load_messages_of_forum(${lesson_id}, ${startswith}, ${endswith})" style="margin-bottom: 15px; margin-bottom: 15px; background: none; border: none; text-decoration: underline; color: #19198e; cursor: pointer; margin: 20px; margin-bottom: 50px">Загрузить больше сообщений</button>
    `
  }
}

function show_nested_messages(parent_message_id, messages, no_more_nested_messages, startswith, endswith) {
  var messages_block = document.getElementById("parent_message_" + parent_message_id)
  for (var i = 0; i < messages.length; i++) {
    messages_block.innerHTML += `
      <div class="usersAns" id="message_${parent_message_id}_${messages[i]["pk"]}">
        <div class="userImg">
          <button style="background-image: url(${messages[i]["fields"]["user_img"]})" type="button" class="image_btn"></button>
        </div>
        <div class="user">
          <p style="color: #4E9F3D; font-weight: bold; margin: 0" class="username">${messages[i]["fields"]["user"]}</p>

          <div class="rating">
            <span>${messages[i]["fields"]["date"]}</span>
          </div>

          <p style="margin: 10px 0">${messages[i]["fields"]["comment"]} <a onclick="set_answer_form(${parent_message_id}, ${messages[i]["pk"]})">Ответить</a></p>
        </div>
      </div>
    `
    if (i != 0) {
      messages_block.innerHTML += `<hr>`
    }
  }
  if (!no_more_nested_messages) {
    messages_block.innerHTML += `
      <button onclick="this.style.display = 'none'; load_nested_messages_of_forum(${parent_message_id}, ${startswith}, ${endswith})" style="margin-bottom: 15px; margin-bottom: 15px; background: none; border: none; text-decoration: underline; color: #19198e; cursor: pointer;">Загрузить больше сообщений</button>
    `
  }
}

function cancel_answer_form() {
  var parent_message_id = document.getElementById(`parent_comment_id_${current_lesson_id}`)
  var nested_message_id = document.getElementById(`nested_comment_id_${current_lesson_id}`)
  parent_message_id.value = 0
  nested_message_id.value = 0

  var to_whom_answer_blocks = document.getElementsByClassName("to_whom_answer_block")
  for (var i = 0; i < to_whom_answer_blocks.length; i++) {
    to_whom_answer_blocks[i].style.display = "none"
  }
}

function set_answer_form(comment_id, nested_comment_id=0) {
  var parent_message_id = document.getElementById(`parent_comment_id_${current_lesson_id}`)
  var nested_message_id = document.getElementById(`nested_comment_id_${current_lesson_id}`)
  parent_message_id.value = comment_id
  nested_message_id.value = nested_comment_id

  var to_whom_answer_blocks = document.getElementsByClassName("to_whom_answer_block")
  var block = document.getElementById(`message_${comment_id}_${nested_comment_id}`)
  var username = block.getElementsByClassName("username")[0]
  for (var i = 0; i < to_whom_answer_blocks.length; i++) {
    to_whom_answer_blocks[i].style.display = "block"
    var whom = to_whom_answer_blocks[i].getElementsByClassName("whom")[0]
    whom.innerText = username.innerText
    whom.href = `#message_${comment_id}_${nested_comment_id}`
  }
}
