function show_coupon_form_errors(errors) {
	var coupon_form_errors = document.getElementById('coupon_form_errors');
	coupon_form_errors.innerHTML = "";
	var txt = "<ul>";

	if (!errors) {
		alert("You were logged in by another device so this device was unauthorized");
	}

	Object.keys(errors).forEach((key) => {
	txt += "<li>" + errors[key] + "</li>";
	})

	coupon_form_errors.innerHTML = txt + "</ul>";
}


$("#coupon_form").submit(function (event) {
	event.preventDefault();
	var formData = new FormData();
	formData.append('csrfmiddlewaretoken', $('#coupon_form input[name="csrfmiddlewaretoken"]').val());
	formData.append("coupon", $("#id_coupon").val());

	$.ajax({
	type: "POST",
	url: "coupon/",
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
			window.location.replace(response["url"]);
		}
		else {
			show_coupon_form_errors(response["errors"])
		}
	},
	error: (xhr, error) => {
		if (xhr.status == 404) {
			show_coupon_form_errors({"not_found": "Такой купон не найден или уже занят"})
		} else if (error = "parsererror") {
			window.location.href = "/courses/user/profile/"
		}
	}
	})

});



const use_cashback_checkbox = document.getElementById("id_use_cashback");
if (use_cashback_checkbox) {
	let course_price_html = document.getElementById("course_price");
	let course_price = parseInt(course_price_html.innerText);
	let cashback_html = document.getElementById("cashback");
	let cashback = parseInt(cashback_html.innerText);

	use_cashback_checkbox.addEventListener('change', function() {
	  if (this.checked) {
	  	if (course_price - cashback <= 0) {
		    course_price_html.innerText = "Бесплатно";
	  	}
	  	else {
		    course_price_html.innerText = course_price - cashback + "тг";
	  	}
	  } else {
	    course_price_html.innerText = course_price + "тг"
	  }
	});
}
