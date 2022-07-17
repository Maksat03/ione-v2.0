const slider = {};

var temp_slider = document.getElementsByClassName('carousel-top');
for (var i = 0; i < temp_slider.length; i++) {
	slider[temp_slider[i].id] = {"slides": temp_slider[i].getElementsByClassName("item"), "current": 0, "prev": 4, "next": 1};
}

function gotoNum(id) {
	if (slider[id]["next"] == 5) {
    slider[id]["next"] = 0;
  }
  if (slider[id]["prev"] == -1) {
    slider[id]["prev"] = 4;
  }

  var preprev = slider[id]["prev"] - 1;
  var nenext = slider[id]["next"] + 1;

	for (let i = 0; i < slider[id]["slides"].length; i++) {
		slider[id]["slides"][i].classList.remove("active");
		slider[id]["slides"][i].classList.remove("prev");
		slider[id]["slides"][i].classList.remove("next");
    slider[id]["slides"][i].classList.remove("preprev");
		slider[id]["slides"][i].classList.remove("nenext");
	}

	if (nenext == 5) {
		nenext = 0;
	}

	if (preprev == -1) {
		preprev = 4;
	}

	if (slider[id]["current"] == true) {
		slider[id]["slides"][1].classList.add("active");
	}
	else if (slider[id]["current"] == false) {
		slider[id]["slides"][0].classList.add("active");
	}
	else {
		slider[id]["slides"][slider[id]["current"]].classList.add("active");
	}
	slider[id]["slides"][slider[id]["prev"]].classList.add("prev");
	slider[id]["slides"][slider[id]["next"]].classList.add("next");
  slider[id]["slides"][preprev].classList.add("preprev");
	slider[id]["slides"][nenext].classList.add("nenext");
}

function gotoPrev(btn) {
	if (slider[btn.id]['current'] <= 0) {
		slider[btn.id]['current'] = slider[btn.id]["slides"].length - 1;
	}
	else {
		slider[btn.id]['current'] -= 1;
	}
	slider[btn.id]['prev'] = slider[btn.id]["current"] - 1;
	slider[btn.id]['next'] = slider[btn.id]["current"] + 1;

	gotoNum(btn.id);
}

function gotoNext(btn) {
	if (slider[btn.id]['current'] >= 4) {
		slider[btn.id]['current'] = 0;
	}
	else {
		slider[btn.id]['current'] += 1;
	}
	slider[btn.id]['prev'] = slider[btn.id]["current"] - 1;
	slider[btn.id]['next'] = slider[btn.id]["current"] + 1;

	gotoNum(btn.id);
}