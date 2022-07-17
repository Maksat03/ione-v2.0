var btns = document.getElementsByClassName("btn");

function open_fav_authors() {
  btns[0].value = 0
  btns[1].value = 1
  var authors = document.getElementById("authors");
  authors.style.display = "none";
  var fav_authors = document.getElementById("fav_authors");
  fav_authors.style.display = "block";
}

function open_authors_list() {
  btns[0].value = 1
  btns[1].value = 0
  var authors = document.getElementById("authors");
  authors.style.display = "block";
  var fav_authors = document.getElementById("fav_authors");
  fav_authors.style.display = "none";
}


var fav_btns = document.getElementsByClassName("fav_btn");
for (var i = 0; i < fav_btns.length; i++) {
  if (fav_btns[i].value % 2 == 1) {
    fav_btns[i].style.backgroundImage = 'url(/static/css/details/imgs/Library/like1.png)';
  }
  else {
    fav_btns[i].style.backgroundImage = 'url(/static/css/details/imgs/Library/like.png)';
  }
}

function add_to_favourite(el){
  $.ajax({
    url: `add_to_favourite/${el.id}/`,
    type: "POST",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": $.cookie("csrftoken"),
    },
    success: (response) => {
      if (response["success"]){
        el.style.backgroundImage = "url('/static/css/details/imgs/Library/like1.png')";
        var node = document.getElementById("author_"+el.id);
        var clone = node.cloneNode(true);
        clone.id = "fav_author_" + el.id;
        var fav_authors = document.getElementById("fav_authors");
        fav_authors.appendChild(clone);
      }
    },
    error: (error) => {
      console.log(error);
    }
  });
}

function remove_from_favourite(el){
  $.ajax({
    url: `remove_from_favourite/${el.id}/`,
    type: "POST",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": $.cookie("csrftoken"),
    },
    success: (response) => {
      if (response["success"]){
        var author = document.getElementById("author_"+el.id);
        if (author) {
          var btn = author.getElementsByClassName("fav_btn")[0];
          btn.style.backgroundImage = "url('/static/css/details/imgs/Library/like.png')";
          btn.value = 0;
        }
        var fav_author = document.getElementById("fav_author_"+el.id);
        var fav_authors = document.getElementById('fav_authors')
        fav_authors.removeChild(fav_author);
        
      }
    },
    error: (error) => {
      console.log(error);
    }
  });
}

function Listener(btn) {
  btn.value++;
  if (btn.value % 2 == 1) {
    btn.style.backgroundImage = 'url(/static/css/details/imgs/Library/like1.png)';
    add_to_favourite(btn);
  }
  else {
    btn.style.backgroundImage = 'url(/static/css/details/imgs/Library/like.png)';
    remove_from_favourite(btn);
  }
}