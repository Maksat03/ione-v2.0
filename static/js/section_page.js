let loading = document.getElementsByClassName('loading')[0];
let courses_cards = $(".courses-cards");
courses_cards.remove(loading);

let get_courses_by = {
    "filter_by": {
      "course__rating__gte": {
        "type": "float",
        "values_for_filtering": []
      },
      "language": {
        "type": "integer",
        "values_for_filtering": []
      },
      "has_homeworks": {
        "type": "boolean-radio",
        "values_for_filtering": []
      },
      "has_subtitles": {
        "type": "boolean-radio",
        "values_for_filtering": []
      },
      "is_free": {
        "type": "boolean-checkbox",
        "values_for_filtering": []
      }
    },
    "endswith": 5,
    "no_more_course": false,
    "success": false
};

function add_to_favourite(el) {
  $.ajax({
    url: "course/" + el.id + "/add_to_favourite/",
    type: "POST",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": $.cookie("csrftoken"),
    },
    success: (response) => {
      if (response["success"]){
        el.style.backgroundImage = "url('/static/css/details/imgs/Library/like1.png')";
      }
    },
    error: (error) => {
      console.log(error);
    }
  });
}

function remove_from_favourite(el) {
  $.ajax({
    url: "course/" + el.id + "/remove_from_favourite/",
    type: "POST",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": $.cookie("csrftoken"),
    },
    success: (response) => {
      if (response["success"]){
        el.style.backgroundImage = "url('/static/css/details/imgs/Library/like.png')";
      }
    },
    error: (error) => {
      console.log(error);
    }
  });
}

function listener(el) {
  el.value++;
  console.log(el.value);
  if (el.value % 2 == 1) {
    add_to_favourite(el);
  }
  else {
    remove_from_favourite(el);
  }
}

function show_courses_list(courses) {
  courses_cards.html("");
  for (var i = 0; i < courses.length; i++) {
    var rating = `<div class="rating"><h3>${courses[i]["fields"]["rating"]}`
    for (var j = 0; j < parseInt(courses[i]["fields"]["rating"]); j++) {
      var rating_img = document.createElement("img");
      rating_img.src = "/static/css/details/imgs/lessonsPage/fullStar.png";
      rating_img.alt = "";
      rating += rating_img.outerHTML;
    }
    if (courses[i]["fields"]["rating"] - Math.floor(courses[i]["fields"]["rating"]) >= 0.5) {
      var rating_img = document.createElement("img");
      rating_img.src = "/static/css/details/imgs/lessonsPage/halfStar.png";
      rating_img.alt = "";
      rating += rating_img.outerHTML;
    }
    for (var j = 0; j < 5 - Math.round(courses[i]["fields"]["rating"]); j++) {
      var rating_img = document.createElement("img");
      rating_img.src = "/static/css/details/imgs/lessonsPage/noStar.png";
      rating_img.alt = "";
      rating += rating_img.outerHTML;
    }
    rating += `</h3></div>`
    var whole_text = "";
    for (var author_i = 0; author_i < courses[i]["fields"]["authors"].length; author_i++) {
      text = `<a href="${courses[i]["fields"]["authors"][author_i]["url"]}">${courses[i]["fields"]["authors"][author_i]["name"]}</a>`;
      if (author_i + 1 != courses[i]["fields"]["authors"].length) {
        text += ", ";
      }
      else {
         text += ". ";
      }
      whole_text += text;
    }

    courses_cards.html(courses_cards.html() + `<div class="card">
      <div onclick="window.location.href = 'course/${courses[i]["pk"]}/'" style="display: flex;" style="width: 100%;" class="cardInf_block_div">
        <img src="/media/${courses[i]["fields"]["poster"]}" alt="">
        <div class="cardInf_block" style="width: 100%;">
          <div class="cardInf">
            <h3>${courses[i]["fields"]["title"]}</h3>
            <span>${courses[i]["fields"]["description"]}</span>
            <p class="authors">${whole_text}</p>
            ${rating}
            <p>всего ${courses[i]["fields"]["video_duration"]} ч - ${courses[i]["fields"]["number_of_lessons"]} лекции</p>
          </div>
          <div class="price">
            <h3>${courses[i]["fields"]["is_free"] ? "Бесплатно" : parseInt(courses[i]["fields"]["current_price"])+"тг"}</h3>
          </div>
        </div>
      </div>
      <div class="select">
        <button onclick="listener(this)" id="${courses[i]["pk"]}" value="${courses[i]["fields"]["is_favourite"] ? 1 : 0}" style="background-image: url(${courses[i]["fields"]["is_favourite"] ? '/static/css/details/imgs/Library/like1.png' : '/static/css/details/imgs/Library/like.png'});">
        </button>
      </div>
    </div>
    <hr>`) // data-title="Добавить в избранные"
  }
}

function get_courses() {
  get_courses_by["order_by"] = document.getElementById('order_by').value;
  get_courses_by["success"] = false;
  courses_cards.append(loading);
  if (!(get_courses_by["no_more_course"])) {
    $.ajax({
      url: "get_courses/",
      type: "POST",
      dataType: "json",
      data: JSON.stringify(get_courses_by),
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": $.cookie("csrftoken"),
      },
      success: (response) => {
        if (response["success"]){
          courses_cards.remove(loading);
          show_courses_list(response["courses"]);
          get_courses_by["no_more_course"] = response["no_more_course"];
          if (!(get_courses_by["no_more_course"])) {
            get_courses_by["endswith"] += 5;
          }
          get_courses_by["success"] = true;
          document.getElementById('order_by').value = get_courses_by["order_by"];
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


function checkbox_action(el) {
  var value = el.getAttribute("data-value");
  if (get_courses_by["filter_by"][el.name]["type"] == "float") {
    value = parseFloat(value);
  }
  else if (get_courses_by["filter_by"][el.name]["type"] == "boolean-radio" || get_courses_by["filter_by"][el.name]["type"] == "boolean-checkbox") {
    value = (value === 'true');
  }
  else if (get_courses_by["filter_by"][el.name]["type"] == "integer") {
    value = parseInt(value);
  }

  if (get_courses_by["filter_by"][el.name]["type"] == "boolean-radio") {
    var radios = document.getElementsByName(el.name);
    
    for (var i = 0; i < 2; i++) {
      if (radios[i].getAttribute("data-value") == el.getAttribute("data-value")) {
        var index = Math.abs(i - 1);
      }
    }

    el.value++;

    el.checked = el.value % 2;
    
    if (!(el.checked == false && radios[index].checked == false)) {
      radios[index].checked = !el.checked;
      radios[index].value = el.value - 1;
    }

    if (el.checked) {
      get_courses_by["filter_by"][el.name]["values_for_filtering"].splice(0, 1);
      get_courses_by["filter_by"][el.name]["values_for_filtering"].push(value);
    }
    else if (radios[index].checked) {
      value = radios[index].getAttribute("data-value");
      value = (value === 'true');
      get_courses_by["filter_by"][el.name]["values_for_filtering"].splice(0, 1);
      get_courses_by["filter_by"][el.name]["values_for_filtering"].push(value);      
    }
    else {
      get_courses_by["filter_by"][el.name]["values_for_filtering"].splice(0, 1);
    }

  }
  else {
    if (get_courses_by["filter_by"][el.name]["values_for_filtering"].includes(value)) {
      var indexOfElValue = get_courses_by["filter_by"][el.name]["values_for_filtering"].indexOf(value);
      get_courses_by["filter_by"][el.name]["values_for_filtering"].splice(indexOfElValue, 1);
    }
    else {
      get_courses_by["filter_by"][el.name]["values_for_filtering"].push(value);
    }
  }
  get_courses_by["endswith"] = 5;
  get_courses_by["no_more_course"] = false;
  get_courses();

}

window.onscroll = function() {
  if (!get_courses_by["no_more_course"] && get_courses_by["success"]) {
    if (window.scrollY + window.innerHeight + 630 >= document.body.scrollHeight) {
      get_courses();
    }
  }
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



document.getElementById('order_by').addEventListener('change', function(){
    if (get_courses_by["no_more_course"] == false) {
      get_courses_by["endswith"] -= 5;
    }
    else {
      get_courses_by["no_more_course"] = false;
    }
    get_courses();
});



get_courses();