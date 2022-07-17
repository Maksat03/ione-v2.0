var current_opened_category_id = 0
var current_selected_btn = document.getElementsByClassName("btn")[0]

function open_category(id, element) {
    if (current_opened_category_id != 0) {
        document.getElementById("section_"+current_opened_category_id).style.display = "none"
    }
    document.getElementById("section_"+id).style.display = "block"
    current_opened_category_id = id
    current_selected_btn.value = 0
    element.value = 1
    current_selected_btn = element
}

function add_to_favourite(el) {
  $.ajax({
    url: "search/course/" + el.id + "/add_to_favourite/",
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
    url: "search/course/" + el.id + "/remove_from_favourite/",
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

function Listener(el) {
  el.value++;
  console.log(el.value);
  if (el.value % 2 == 1) {
    add_to_favourite(el);
  }
  else {
    remove_from_favourite(el);
  }
}