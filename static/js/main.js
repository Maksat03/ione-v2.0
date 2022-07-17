let scrollUp = document.getElementsByClassName('scrollUp')[0];
const anchors = document.querySelectorAll('a[href*="#scroll"]')

for (let anchor of anchors) {
  anchor.addEventListener('click', function(event) {
    event.preventDefault();
    const blockID = anchor.getAttribute('href');
    document.querySelector('' + blockID).scrollIntoView({
      behavior: "smooth",
      block: "start"
    })
  })
}

window.onscroll = function() {
  if (window.scrollY >= 1500) {
    scrollUp.style.display = "block";
  }
  else {
    scrollUp.style.display = "none";
  }
  if (window.scrollY + window.innerHeight + 200 >= document.body.scrollHeight) {
    scrollUp.style.marginBottom = (window.scrollY + window.innerHeight + 200) - document.body.scrollHeight + "px";
  }
  else {
   scrollUp.style.marginBottom = "0px";
  }
};

$(".categories-dropdown-btn").click(function(event) {
  if (this.value === undefined) {
    this.value = 0
  }
  if (this.value == 0) {
    this.parentNode.getElementsByClassName('categories')[0].style.display = "block"
    this.value++;
  } else {
    this.parentNode.getElementsByClassName("categories")[0].style.display = "none";
    var btns = document.getElementsByClassName("category_btn")
    for (var i = btns.length - 1; i >= 0; i--) {
      btns[i].value = 0
    }
    var subcategories = document.getElementsByClassName("subcategories")
    for (var i = subcategories.length - 1; i >= 0; i--) {
      subcategories[i].style.display = "none"
    }
    this.value--;
  }
})

$(".dropbtn").click(function(event) {
  if (this.value === undefined) {
    this.value = 0
  }
  if (this.value == 0) {
    document.getElementsByClassName("dropdown-content")[0].style.display = "block"
    this.value++;
  } else {
    document.getElementsByClassName("dropdown-content")[0].style.display = "none"
    this.value--;
  }
})

$(".category_btn").click(function(event) {
  if (this.value === undefined) {
    this.value = 0
  }
  if (this.value == 0) {
    var parent = this.parentNode
    while (parent.className != "nav") {
      if (parent.id == "categories") {
        this.parentNode.getElementsByClassName("subcategories")[0].style.display = "inline-block";
        break
      } else if (parent.id == "mob_categories") {
        this.parentNode.getElementsByClassName("subcategories")[0].style.display = "block";
        break
      } else {
        parent = parent.parentNode
      }
    }
    var children = this.parentNode.parentNode.children
    for (var i = children.length - 1; i >= 0; i--) {
      if (children[i].className == "category" && children[i] != this.parentNode) {
        var subcategories = children[i].getElementsByClassName("subcategories")
        var btns = children[i].getElementsByClassName("category_btn")
        for (var i = btns.length - 1; i >= 0; i--) {
          btns[i].value = 0
        }
        for (var i = subcategories.length - 1; i >= 0; i--) {
          subcategories[i].style.display = "none"
        }
      }
    }
    this.value++;
  } else {
    var subcategories = this.parentNode.getElementsByClassName("subcategories")
    for (var i = subcategories.length - 1; i >= 0; i--) {
      subcategories[i].style.display = "none"
    }
    var btns = this.parentNode.getElementsByClassName("category_btn")
    for (var i = btns.length - 1; i >= 0; i--) {
      btns[i].value = 0
    }
  }  
})

function erase_registration_form_errors() {
  var fields = ["first_name", "last_name", "email", "password1", "password2", "user_agreement", "phone_number"]
  fields.forEach((field) => {
    var field_errors = document.getElementById(field + '_field_errors');
    field_errors.innerHTML = "";
  })
}


function show_registration_form_errors(errors) {
  erase_registration_form_errors();
  Object.keys(errors).forEach((key) => {
    var field_errors = document.getElementById(key + '_field_errors');
    var txt = "<ul>";

    for (var i = errors[key].length - 1; i >= 0; i--) {
      txt += "<li>" + errors[key][i]["message"] + "</li>";
    }

    field_errors.innerHTML = txt + "</ul>";
  })
}




$(".registration_form").submit(function (event) {
  var formData = {
    csrfmiddlewaretoken: $('.registration_form input[name="csrfmiddlewaretoken"]').val(),
    first_name: $("#id_first_name").val(),
    last_name: $("#id_last_name").val(),
    email: $("#id_email").val(),
    password1: $("#id_password1").val(),
    password2: $("#id_password2").val(),
    user_agreement: $("#id_user_agreement").prop('checked'),
    phone_number: $("#id_phone_number").val()
  };

  document.getElementsByClassName("reg_button")[0].disabled = true;

  $.ajax({
    type: "POST",
    url: "/courses/user/sign-up/",
    data: JSON.stringify(formData),
    dataType: "json",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": $.cookie("csrftoken"),
    },
    success: (response) => {
      if (response["success"]) {
        alert('Чтобы предотвратить неправильное использование, пожалуйста, подтвердите, что вы являетесь человеком. Введите код подтверждения, отправленный на ' + formData["email"] +'. Если сообщения нет в папке "Входящие! - проверьте, не попало ли оно в папку "спам".');
        document.getElementsByClassName("reg_button")[0].disabled = false;
      }
      else {
        show_registration_form_errors(response["errors"]);
      }
    },
    error: (error) => {
      console.log(error);
    }
  })

  event.preventDefault();
});



function show_login_form_errors(errors) {
  var login_form_errors = document.getElementById('login_form_errors');
  login_form_errors.innerHTML = "";
  var txt = "<ul>";

  Object.keys(errors).forEach((key) => {
    txt += "<li>" + errors[key] + "</li>";
  })

  login_form_errors.innerHTML = txt + "</ul>";
}




$(".login_form").submit(function (event) {
  var formData = {
    csrfmiddlewaretoken: $('.login_form input[name="csrfmiddlewaretoken"]').val(),
    username: $("#id_username").val(),
    password: $("#id_password").val()
  };

  $.ajax({
    type: "POST",
    url: "/courses/user/login/",
    data: JSON.stringify(formData),
    dataType: "json",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": $.cookie("csrftoken"),
    },
    success: (response) => {
      if (response["success"]) {
        location.href = "/courses/user/profile/";
      }
      else {
        show_login_form_errors(response["errors"]);
      }
    },
    error: (error) => {
      console.log(error);
    }
  })

  event.preventDefault();
});



function show_reset_password_form_errors(errors) {
  var reset_password_form_errors = document.getElementById('reset_password_email_field_errors');
  reset_password_form_errors.innerHTML = "";
  var txt = "<ul>";

  Object.keys(errors).forEach((key) => {
    txt += "<li>" + errors[key] + "</li>";
  })

  reset_password_form_errors.innerHTML = txt + "</ul>";
}




$(".reset_password_form").submit(function (event) {
  var formData = {
    csrfmiddlewaretoken: $('.reset_password_form input[name="csrfmiddlewaretoken"]').val(),
    reset_password_email_field: $("#id_reset_password_email_field").val(),
  };

  $.ajax({
    type: "POST",
    url: "/courses/user/reset_password/",
    data: JSON.stringify(formData),
    dataType: "json",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": $.cookie("csrftoken"),
    },
    success: (response) => {
      if (response["success"]) {
        alert("На ваш эл почту был отправлен ссылка где вы можете написать новый пароль для своего аккаунта");
      }
      else {
        show_reset_password_form_errors(response["errors"]);
      }
    },
    error: (error) => {
      console.log(error);
    }
  })

  event.preventDefault();
});


function erase_publish_course_request_form_errors() {
  var fields = ["teacher_first_name", "teacher_last_name", "teacher_phone_number", "teacher_course_direction"]
  fields.forEach((field) => {
    var field_errors = document.getElementById(field + '_field_errors');
    field_errors.innerHTML = "";
  })
}


function show_publish_course_request_form_errors(errors) {
  erase_publish_course_request_form_errors();
  Object.keys(errors).forEach((key) => {
    var field_errors = document.getElementById(key + '_field_errors');
    var txt = "<ul>";

    if (key == "teacher_phone_number") {
      txt += "<li>" + "Введите действительный номер телефона (например, +77081235467). Номер должен начинаться с +7" + "</li>";
    } else {
      for (var i = errors[key].length - 1; i >= 0; i--) {
        txt += "<li>" + errors[key][i] + "</li>";
      }
    }

    field_errors.innerHTML = txt + "</ul>";
  })
}



$("#publish_course_request_form").submit(function (event) {
  var formData = new FormData();
  formData.append('csrfmiddlewaretoken', $('#publish_course_request_form input[name="csrfmiddlewaretoken"]').val());
  formData.append("teacher_phone_number", $("#id_teacher_phone_number").val());
  formData.append("teacher_first_name", $("#id_teacher_first_name").val());
  formData.append("teacher_last_name", $("#id_teacher_last_name").val());
  formData.append("teacher_course_direction", $("#id_teacher_course_direction").val());

  $.ajax({
    type: "POST",
    url: "/teacher/publish_course_request/",
    data: formData,
    dataType: "json",
    processData: false,
    contentType: false,
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": $.cookie("csrftoken"),
    },
    success: (response) => {
      console.log(response)
      if (response["success"]) {
        alert("Ваш запрос успешно отправлен")
      }
      else {
        show_publish_course_request_form_errors(response["errors"])
      }
    },
    error: (xhr, error) => {
      console.log(xhr)
    }
  })

  event.preventDefault()
});