let comments_div = $(".comments_list");
var endswith = 10;
var no_more_comment = false;

function get_rating_stars(rating) {
  var result = '';
  for (var j = 0; j < parseInt(rating); j++) {
    var rating_img = document.createElement("img");
    rating_img.src = "/static/css/details/imgs/lessonsPage/fullStar.png";
    rating_img.alt = "";
    result += rating_img.outerHTML;
  }

  if (rating - Math.floor(rating) >= 0.5) {
    var rating_img = document.createElement("img");
    rating_img.src = "/static/css/details/imgs/lessonsPage/halfStar.png";
    rating_img.alt = "";
    result += rating_img.outerHTML;
  }

  for (var j = 0; j < 5 - Math.round(rating); j++) {
    var rating_img = document.createElement("img");
    rating_img.src = "/static/css/details/imgs/lessonsPage/noStar.png";
    rating_img.alt = "";
    result += rating_img.outerHTML;
  }
  return result;
}

function show_comments(comments) {
  comments_div.html("");
	for (var i = 0; i < comments.length; i++) {
    comments_div.html(comments_div.html() + `
      <div class="comment">
        <div class="usersCom">
          <div class="usersImg">
            <button style="background-image: url(${comments[i]["fields"]["user_photo"]})"></button>
          </div>
          <div class="user">
            <div class="name">
              <p>${comments[i]["fields"]["username"]}</p>
            </div>
            <div class="rating">
              <h3>${comments[i]["fields"]["rating"]}</h3>
              ${get_rating_stars(comments[i]["fields"]["rating"])}
              <span>${comments[i]["fields"]["time"]}</span>
            </div>
            <div class="ratingCom">
              <p>${comments[i]["fields"]["comment"]}</p>
            </div>
          </div>
        </div>
      </div>
      `)
	}
}

function get_comments() {
  if (!no_more_comment) {
    $.ajax({
      url: "get_comments/?endswith=" + endswith,
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": $.cookie("csrftoken"),
      },
      success: (response) => {
        if (response["success"]){
          show_comments(response["comments"]);
          no_more_comment = response["no_more_comment"];
          if (!no_more_comment) {
            endswith += 10;
          }
          else {
            btn.style.display = "none";
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


get_comments();

let btn = document.getElementById('get_comments');
btn.onclick = get_comments;