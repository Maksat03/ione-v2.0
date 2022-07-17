var fav_courses = $(".favourites-cards .card");
var buttons = document.getElementsByClassName("btn");

var fragment = window.location.hash.substr(1);
if (fragment == "favourites") {
  var temp = buttons[0].cloneNode(true);
  buttons[0].name = buttons[buttons.length - 1].name;
  buttons[0].value = buttons[buttons.length - 1].value;
  buttons[0].innerText = buttons[buttons.length - 1].innerText;
  buttons[0].dataset.value = buttons[buttons.length - 1].getAttribute("data-value");
  buttons[0].value = 1;
  document.getElementsByClassName(buttons[0].getAttribute("data-value"))[0].style.display = "block";
    

  buttons[buttons.length - 1].name = temp.name;
  buttons[buttons.length - 1].value = temp.value;
  buttons[buttons.length - 1].innerText = temp.innerText;
  buttons[buttons.length - 1].dataset.value = temp.getAttribute("data-value");
  buttons[buttons.length - 1].value = 0;
  document.getElementsByClassName(buttons[buttons.length - 1].getAttribute("data-value"))[0].style.display = "none";

  window.location.replace("#");
}

function func(el) {
  for (var i = 0; i < buttons.length; i++) {
    if (buttons[i].name == el.name) {
      el.value = 1;
      var section = el.getAttribute("data-value");
      document.getElementsByClassName(section)[0].style.display = "block";
    }
    else {
      buttons[i].value = 0;
      var section = buttons[i].getAttribute("data-value");
      document.getElementsByClassName(section)[0].style.display = "none";
    }
  }
}



function remove_from_favourite(el) {
  $.ajax({
    url: "course/" + el.getAttribute("data-value") + "/remove_from_favourite/",
    type: "POST",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": $.cookie("csrftoken"),
    },
    success: (response) => {
      if (response["success"]){
        for (var i = fav_courses.length - 1; i >= 0; i--) {
          if (fav_courses[i].getAttribute("data-value") == el.getAttribute("data-value")) {
            $(".favourites-cards " + "#" + fav_courses[i].id).remove();
          }
        }
      }
    },
    error: (error) => {
      console.log(error);
    }
  });
}



function progressView(){
  let diagramBox = document.querySelectorAll('.diagram.progress');
  diagramBox.forEach((box) => {
      let deg = (360 * box.dataset.percent / 100) + 180;
      if(box.dataset.percent >= 50){
          box.classList.add('over_50');
      }else{
          box.classList.remove('over_50');
      }
      box.querySelector('.piece.right').style.transform = 'rotate('+deg+'deg)';
  });
}
progressView();


let view_coupon_form = document.getElementById("view_coupon");
let view_coupon_btns = document.querySelectorAll('a[href="#view_coupon"]');
let coupon_courses_titles = document.getElementsByClassName("coupon_course_title");

for (var i = view_coupon_btns.length - 1; i >= 0; i--) {
  view_coupon_btns[i].onclick = function() {
    for (var j = coupon_courses_titles.length - 1; j >= 0; j--) {
      if (coupon_courses_titles[j].id == this.id) {
        view_coupon_form.getElementsByClassName("coupon_form_info_course_name")[0].innerText = coupon_courses_titles[j].innerText;
        view_coupon_form.getElementsByClassName("view_coupon_form_submit_button")[0].id = this.id;
        view_coupon_form.getElementsByClassName("coupon-pass")[0].style.display = 'none';
        view_coupon_form.getElementsByClassName("coupon_number")[0].innerText = "";
        view_coupon_form.getElementsByClassName("view_coupon_form_submit_button")[0].style.display = 'block';
        view_coupon_form.getElementsByClassName("form-fields")[0].style.display = 'block';
        document.getElementById("view_coupon_form_error").innerText = "";
        document.getElementById("id_view_coupon_password").value = "";
        break;
      }
    }
  }
}



$(".view_coupon_form").submit(function (event) {
  var formData = new FormData();
  formData.append('csrfmiddlewaretoken', $('.view_coupon_form input[name="csrfmiddlewaretoken"]').val());
  formData.append("password", $("#id_view_coupon_password").val());
  formData.append("coupon_pk", view_coupon_form.getElementsByClassName("view_coupon_form_submit_button")[0].id);


  $.ajax({
    type: "POST",
    url: "view_coupon/",
    data: formData,
    processData: false,
    contentType: false,
    dataType: "json",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": $.cookie("csrftoken"),
    },
    success: (response) => {
      if (response["success"]) {
        view_coupon_form.getElementsByClassName("coupon-pass")[0].style.display = 'block';
        view_coupon_form.getElementsByClassName("coupon_number")[0].innerText = response["coupon_number"];
        view_coupon_form.getElementsByClassName("view_coupon_form_submit_button")[0].style.display = 'none';
        view_coupon_form.getElementsByClassName("form-fields")[0].style.display = 'none';
        document.getElementById("view_coupon_form_error").innerText = "";
      }
      else {
        if (response["password_is_invalid"]) {
          document.getElementById("view_coupon_form_error").innerText = "Password is invalid";
        }
        else if (response["errors"]["unauthorized"]) {
          document.getElementById("view_coupon_form_error").innerText = "You were logged in by another device so this device was unauthorized";
        }
      }
    },
    error: (error) => {
      console.log(error);
    }
  })

  event.preventDefault();
});




function erase_change_user_data_form_errors() {
  var fields = ["first_name", "last_name", "phone_number", "date_of_birth", "photo"]
  fields.forEach((field) => {
    var field_errors = document.getElementById(field + '_field_errors');
    field_errors.innerHTML = "";
  })
}


function show_change_user_data_form_errors(errors) {
  erase_change_user_data_form_errors();
  Object.keys(errors).forEach((key) => {
    var field_errors = document.getElementById(key + '_field_errors');
    var txt = "<ul>";

    for (var i = errors[key].length - 1; i >= 0; i--) {
      txt += "<li>" + errors[key][i]["message"] + "</li>";
    }

    field_errors.innerHTML = txt + "</ul>";
  })
}




$(".change_user_data_form").submit(function (event) {
  var formData = new FormData();
  formData.append('csrfmiddlewaretoken', $('.change_user_data_form input[name="csrfmiddlewaretoken"]').val());
  formData.append("first_name", $("#id_first_name").val());
  formData.append("last_name", $("#id_last_name").val());
  formData.append("phone_number", $("#id_phone_number").val());
  formData.append("date_of_birth", $("#id_date_of_birth").val());
  formData.append('photo', $("#id_photo")[0].files[0]);

  $.ajax({
    type: "POST",
    url: "change_user_data/",
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
        location.href = "/courses/user/profile/";
      }
      else {
        show_change_user_data_form_errors(response["errors"]);
      }
    },
    error: (error) => {
      console.log(error);
    }
  })

  event.preventDefault();
});


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


function erase_change_email_form_errors() {
  var fields = ["password", "email"]
  fields.forEach((field) => {
    var field_errors = document.getElementById(field + '_field_errors');
    field_errors.innerHTML = "";
  })
}


function show_change_email_form_errors(errors) {
  erase_change_email_form_errors();
  Object.keys(errors).forEach((key) => {
    var field_errors = document.getElementById(key + '_field_errors');
    var txt = "<ul>";

    for (var i = errors[key].length - 1; i >= 0; i--) {
      txt += "<li>" + errors[key][i] + "</li>";
    }

    field_errors.innerHTML = txt + "</ul>";
  })
}




$(".change_email_form").submit(function (event) {
  var formData = new FormData();
  formData.append('csrfmiddlewaretoken', $('.change_email_form input[name="csrfmiddlewaretoken"]').val());
  formData.append("password", $(".change_email_form #id_password").val());
  formData.append("email", $(".change_email_form #id_email").val());

  $.ajax({
    type: "POST",
    url: "change-email/",
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
        document.getElementsByClassName("change-email-form-container")[0].innerText = "На новый эл почту был отправлен подтверждащая ссылка, перейдите по ссылке и ваша эл почта будет изменена";
      }
      else {
        show_change_email_form_errors(response["errors"]);
      }
    },
    error: (error) => {
      console.log(error);
    }
  })

  event.preventDefault();
});


