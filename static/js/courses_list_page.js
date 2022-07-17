var url = new URL(location.href);
let search = url.searchParams.get("search");
let endswith = 5;
let success = false;
let no_more_course = false;
let courses_cards = $(".courses-cards");
let loading = document.getElementsByClassName('loading')[0];
courses_cards.remove(loading);

function listener(el) {
  el.value++;
  if (el.value % 2 == 1) {
    add_to_favourite(el);
  }
  else {
    remove_from_favourite(el);
  }
}

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
    <hr>`) //  data-title="Добавить в избранные"
  }
}

function get_courses() {
  courses_cards.append(loading);
  success = false;
  if (!(no_more_course)) {
    $.ajax({
      url: `/courses/search-api/?search=${search}&endswith=${endswith}`,
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
      success: (response) => {
        courses_cards.remove(loading);
        show_courses_list(response["courses"]);
        no_more_course = response["no_more_course"];
        if (!(no_more_course)) {
          endswith += 5;
        }
        success = true;
      },
      error: (error) => {
        console.log(error);
      }
    });
  }
}



window.onscroll = function() {
  if (!no_more_course && success) {
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



get_courses();