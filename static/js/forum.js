let comments_div = $(".comments-form > .comments_list");
const csrfmiddlewaretoken = $.cookie("csrftoken");

function show_nested_comments(parent_comment, comments, startswith, endswith, no_more_nested_comment) {
  var comments_block = document.getElementById("user"+parent_comment)
  var get_nested_comments_btn = document.getElementById("get_nested_comments_btn"+parent_comment)
  var answer_to_nested_comment = document.getElementById("answer_to_nested_comment"+parent_comment)
  if (get_nested_comments_btn) {
    comments_block.removeChild(get_nested_comments_btn)
  }
  if (answer_to_nested_comment) {
    comments_block.removeChild(answer_to_nested_comment)
  }
	for (var i = 0; i < comments.length; i++) {
		comments_block.innerHTML += `
        <div class="comAnswer">
          <div class="usersAns">
            <div class="userImg">
              <button style="background-image: url(${comments[i]["fields"]["user"]["image"]}); width: 35px; height: 35px;"></button>
            </div>
    
            <div class="user">
              <p style="color: #4E9F3D; font-weight: bold; margin: 0">${comments[i]["fields"]["user"]["first_name"]} ${comments[i]["fields"]["user"]["last_name"]}</p>
    
              <div class="rating">
                <span style="font-size: 13px; opacity: 0.7;">${comments[i]["fields"]["date"]}</span>
              </div>
    
              <p onclick="display_form(${parent_comment}, '${comments[i]["fields"]["user"]["first_name"] + " " + comments[i]["fields"]["user"]["last_name"] + ", "}')" style="margin: 10px 0">${comments[i]["fields"]["comment"]} <a>Ответить</a></p>
            </div>
          </div>
        </div>
        `
	}
  if (!no_more_nested_comment) {
    comments_block.innerHTML += `<button class="get_comments" data-id="${parent_comment}" id="get_nested_comments_btn${parent_comment}" onclick="get_comments(this, true)" data-no-more-comment="false" data-startswith="${startswith}" data-endswith="${endswith}">Показать еще отзывы</button>`
  }
  var txt = `
    <form action="forum/answer/" method="post" id="answer_to_nested_comment${parent_comment}" style="display: none;">
      <div class="ans">
        <input type="hidden" name="csrfmiddlewaretoken" value="${csrfmiddlewaretoken}">
        <input type="hidden" name="parent_comment_id" class="parent_comment" value="">
        <textarea class="input" name="comment" rows="2" cols="40" placeholder="Ответить" maxlength="10000" required=""></textarea>
  `
  if (typeof is_trial_lesson === 'undefined') {
    let is_trial_lesson = false;
  }

  if (is_trial_lesson) {
    txt += `
    <button class="button" type="button" onclick="alert('Чтобы отправить вы должны купить курс')">Отправить</button>
    `
  }
  else {
    txt += `
      <button class="button" type="submit">Отправить</button>
    `
  }

  txt += `
      </div>
    </form>
  `

  comments_block.innerHTML += txt;
}

function show_comments(comments) {
  for (var i = 0; i < comments.length; i++) {
    comments_div.html(comments_div.html() + `
        <div class="usersCom">
          <div class="userImg">
            <button style="background-image: url(${comments[i]["fields"]["user"]["image"]}); width: 45px; height: 45px;"></button>
          </div>
    
          <div class="user" id="user${comments[i]["pk"]}">
            <p style="color: #4E9F3D; font-weight: bold; margin: 0">${comments[i]["fields"]["user"]["first_name"]} ${comments[i]["fields"]["user"]["last_name"]}</p>
    
            <div class="rating">
              <span style="font-size: 14px; opacity: 0.7;">${comments[i]["fields"]["date"]}</span>
            </div>
    
            <p onclick="display_form(${comments[i]["pk"]}, '${comments[i]["fields"]["user"]["first_name"] + " " + comments[i]["fields"]["user"]["last_name"] + ", "}')" style="margin: 10px 0">${comments[i]["fields"]["comment"]} <a>Ответить</a></p>
    
            <hr>
    
            <!-- comAnswer -->
    
          </div>
        </div>
        `)
    if (comments[i]["nested_comments"]) {
      show_nested_comments(comments[i]["pk"], comments[i]["nested_comments"], comments[i]["startswith"], comments[i]["endswith"], comments[i]["no_more_nested_comment"]);
    }
    else {
      var comments_block = document.getElementById("user"+comments[i]["pk"])
      var txt = `
        <form action="forum/answer/" method="post" id="answer_to_nested_comment${comments[i]["pk"]}" style="display: none;">
          <div class="ans">
            <input type="hidden" name="csrfmiddlewaretoken" value="${csrfmiddlewaretoken}">
            <input type="hidden" name="parent_comment_id" class="parent_comment" value="">
            <textarea class="input" name="comment" rows="2" cols="40" placeholder="Ответить" maxlength="10000" required=""></textarea>
       `
      if (typeof is_trial_lesson === 'undefined') {
        let is_trial_lesson = false;
      }

      if (is_trial_lesson) {
        txt += `
        <button class="button" type="button" onclick="alert('Чтобы отправить вы должны купить курс')">Отправить</button>
        `
      }
      else {
        txt += `
          <button class="button" type="submit">Отправить</button>
        `
      }

      txt += `
          </div>
        </form>
      `

      comments_block.innerHTML += txt;
    }
  }
}

function get_comments(btn, nested=false) {
  if (btn.getAttribute("data-no-more-comment") == "false") {
    var url = "";

    if (nested) {
      url += "forum/get_nested_comments/?parent_comment_id=" + btn.getAttribute("data-id") + "&";
    }
    else {
      url += "forum/get_comments/?";
    }

    $.ajax({
      url: url + "startswith=" + btn.getAttribute("data-startswith") + "&endswith=" + btn.getAttribute("data-endswith"),
      headers: {"X-Requested-With": "XMLHttpRequest"},
      success: (response) => {
        if (response["success"]){
          if (nested) {
            show_nested_comments(btn.getAttribute("data-id"), response["comments"], response["startswith"], response["endswith"], response["no_more_comment"]);
          }
          else {
            show_comments(response["comments"]);
            if (!response["no_more_comment"]) {
              btn.setAttribute("data-startswith", btn.getAttribute("data-endswith"));
              btn.setAttribute("data-endswith", parseInt(btn.getAttribute("data-endswith")) + 5);
            }
            else {
              btn.setAttribute("data-no-more-comment", true);
              btn.style.display = "none";
            }
          }
        }
        else {
          console.log(response["message"]);
        }
      },
      error: (error) => {
        console.log(error);
      }
    });
  }
}

let btn_get_comments = document.getElementsByClassName('get_comments')[0];
get_comments(btn_get_comments);



function display_form(form_id, username) {
  var form = document.getElementById(`answer_to_nested_comment${form_id}`)
  form.style.display = "block";
  var textarea = form.getElementsByClassName('input')[0]
  textarea.value = username
  var parent_comment = form.getElementsByClassName('parent_comment')[0]
  parent_comment.value = form_id
}

