import random
import json
from rest_framework.decorators import api_view

from courses import services as course_services
from courses.forms import CoursePaymentForm
from courses.services import get_course_comments_in_range_from_0_to, give_access_to_course_by_coupon, get_coupon
from courses.views import Object
from iOneCourses.models import iOneNews
from ioka import services as ioka_services
from lessonforum.views import get_comments, get_nested_comments
from lessontest.models import CompletedChoice
from my_courses.forms import RenewAccessForm, ForumCommentForm
from my_courses.views import stream
from sections.services import get_courses, _set_course_authors, _set_course_rating, \
	_set_favourite_courses_among_serialized_courses
from sections.templatetags.sections_tags import get_sections_tree
from user import services as auth_services
from user.services import change_user_data, change_email
from .services import *


def home_page_view(request):
	courses = serialize('python', CompletedCourse.objects.filter(is_last_edition=True))
	_set_course_authors(courses)
	_set_course_rating(courses)

	if is_request_user_token_authenticated(request):
		_set_favourite_courses_among_serialized_courses(request.user.favourite_courses.all(), courses)
	elif is_request_user_authenticated_by_api_key(request):
		_set_favourite_courses_among_serialized_courses(None, courses)
	else:
		return JsonResponse({"success": False, "invalid-api-key": "Invalid API-KEY"})

	news_list = list()
	for news in iOneNews.objects.all():
		news_list.append({"new_title": news.title, "new_text": news.text})

	return JsonResponse({"success": True, "courses": courses, "news": news_list})


@api_view(["POST"])
@token_auth_login_required
def change_profile_image(request):
	if photo := request.FILES.get("photo", False):
		request.user.photo = photo
		request.user.save()
		return JsonResponse({"success": True, "photo_url": request.user.photo.url})
	return JsonResponse({"success": False, "404": "Photo not found"})


@token_auth_login_required
def video_stream_view(request):
	if not (course_pk := request.headers.get("course_pk", False)):
		return JsonResponse({"success": False, "course_pk_not_found": "Course Primary Key Not Found"})
	if not (lesson_index := request.headers.get("lesson_index", False)):
		return JsonResponse({"success": False, "lesson_index_not_found": "Lesson Index Not Found"})

	course = get_object_or_404(MyCourse, user_id=request.user.id, pk=course_pk)
	lessons = course.lessons.all()

	if len(lessons) >= lesson_index:
		lesson = lessons[lesson_index - 1]
	else:
		return JsonResponse({"success": False, "lesson_not_found": "Lesson Not Found"})

	return stream(lesson, request.headers.get('range'))


@ione_api_key_required
def trial_lesson_video_stream_view(request):
	if not (course_pk := request.headers.get("course_pk", False)):
		return JsonResponse({"success": False, "course_pk_not_found": "Course Primary Key Not Found"})
	course = get_object_or_404(CompletedCourse, pk=course_pk)
	lesson = course.get_lessons()[0]
	return stream(lesson, request.headers.get("range"))


@ione_api_key_required
def trial_lesson_view(request):
	if not (course_pk := request.headers.get("course_pk", False)):
		return JsonResponse({"success": False, "course_pk_not_found": "Course Primary Key Not Found"})
	course = get_object_or_404(CompletedCourse, pk=course_pk)
	lesson = course.get_lessons()[0]
	return JsonResponse({"success": True, "lesson": serialize("python", lesson)})


@ione_api_key_required
def trial_lesson_forum_get_comments_view(request):
	if not (course_pk := request.GET.get("course_pk", False)):
		return JsonResponse({"success": False, "course_pk_not_found": "Course Primary Key Not Found"})
	course = get_object_or_404(CompletedCourse, pk=course_pk)
	lesson = Object()
	lesson.lesson = course.get_lessons()[0]
	startswith = int(request.GET.get("startswith"))
	endswith = int(request.GET.get("endswith"))
	return get_comments(lesson, startswith, endswith)


@ione_api_key_required
def trial_lesson_forum_get_nested_comments_view(request):
	if not (course_pk := request.GET.get("course_pk", False)):
		return JsonResponse({"success": False, "course_pk_not_found": "Course Primary Key Not Found"})
	course = get_object_or_404(CompletedCourse, pk=course_pk)
	lesson = Object()
	lesson.lesson = course.get_lessons()[0]
	startswith = int(request.GET.get("startswith"))
	endswith = int(request.GET.get("endswith"))
	parent_comment_id = int(request.GET.get("parent_comment_id"))
	return get_nested_comments(lesson, startswith, endswith, parent_comment_id)


@api_view(["POST"])
@token_auth_login_required
def renew_access_view(request, my_course_pk):
	form = RenewAccessForm(request.data)
	if form.is_valid():
		status, order = ioka_services.create_course_renew_access_order(request.user, my_course_pk, float(form.cleaned_data["months"]))
		if status == 201:
			return JsonResponse({"success": True, "checkout_url": order["order"]["checkout_url"]})
		return JsonResponse({"success": False, "ioka_create_order_error": order})
	return JsonResponse({"success": False, "errors": form.errors})


@token_auth_login_required
def final_test_view(request, course_pk):
	course = get_object_or_404(MyCourse, user_id=request.user.id, pk=course_pk)
	if course.has_final_test() and course.get_number_of_completed_lessons() == course.course.get_number_of_lessons():
		try:
			test = course.course.final_test
			questions = list(test.questions.all())
			random.shuffle(questions)
			serialized_questions = serialize('python', questions)
			for i in range(len(serialized_questions)):
				choices = questions[i].choices.all()
				serialized_questions[i]["fields"]["answers_are_radio"] = True
				if choices.filter(is_answer=True).count() > 1:
					serialized_questions[i]["fields"]["answers_are_radio"] = False
				serialized_questions[i]["fields"]["answers"] = serialize("python", choices)
		except ObjectDoesNotExist:
			serialized_questions = None
		return JsonResponse({
			"success": True,
			"course_title": course.course.title,
			"course_pk": course_pk,
			"questions": serialized_questions,
			"timer": course.course.final_test.time_limit_minutes
		})
	else:
		return JsonResponse({"success": False, "final_test_does_not_exist": "Final Test Does Not Exist For That Course"})


@api_view(["POST"])
@token_auth_login_required
def final_test_check_view(request, course_pk):
	course = get_object_or_404(MyCourse, user_id=request.user.id, pk=course_pk)

	try:
		test = course.course.final_test
	except ObjectDoesNotExist:
		test = None

	if test:
		test_questions_id = [question.id for question in test.questions.all()]

		response = {}
		number_of_correct_answers = 0

		for question_id in request.data.keys():
			question_id = int(question_id)
			if question_id in test_questions_id:
				choices_id = [choice.id for choice in CompletedChoice.objects.filter(question_id=question_id, is_answer=True)]
				response[question_id] = False
				if len(choices_id) != len(request.data[str(question_id)]):
					continue

				for choice_id in request.data[str(question_id)]:
					choice_id = int(choice_id)
					if choice_id in choices_id:
						response[question_id] = True
						choices_id.remove(choice_id)
				if len(choices_id) > 0:
					response[question_id] = False
				else:
					number_of_correct_answers += 1
			else:
				return JsonResponse({"success": False, "question_not_found": f"Question with id={question_id} not found in the final test"})

		total = number_of_correct_answers / len(test_questions_id) * 100

		response["total"] = total
		response["course_was_completed"] = False

		if total > 70:
			if not course.is_completed:
				course.make_course_completed()
				response["course_was_completed"] = True
		return JsonResponse({"success": True} | response)
	return JsonResponse({"success": False, "final_test_does_not_exist": "This course does not have a final test"})


@api_view(["POST"])
@token_auth_login_required
def test_check_view(request):
	if not (course_pk := request.data.get("course_pk", [False])):
		return JsonResponse({"success": False, "course_pk_not_found": "Course Primary Key Not Found"})
	if not (lesson_index := request.data.get("lesson_index", [False])):
		return JsonResponse({"success": False, "lesson_index_not_found": "Lesson Index Not Found"})

	course = get_object_or_404(MyCourse, user_id=request.user.id, pk=course_pk[0])
	lesson_index = lesson_index[0]
	lessons = course.lessons.all()

	if len(lessons) >= lesson_index:
		lesson = lessons[lesson_index - 1]
	else:
		return JsonResponse({"success": False, "lesson_not_found": "Lesson not found"})

	try:
		test = lesson.lesson.test
	except ObjectDoesNotExist:
		test = None

	if test:
		del request.data["course_pk"], request.data["lesson_index"]
		test_questions_id = [question.id for question in test.questions.all()]

		response = {"success": True}
		number_of_correct_answers = 0

		for question_id in request.data.keys():
			question_id = int(question_id)
			if question_id in test_questions_id:
				choices_id = [choice.id for choice in CompletedChoice.objects.filter(question_id=question_id, is_answer=True)]
				response[question_id] = False
				if len(choices_id) != len(request.data[str(question_id)]):
					continue

				for choice_id in request.data[str(question_id)]:
					choice_id = int(choice_id)
					if choice_id in choices_id:
						response[question_id] = True
						choices_id.remove(choice_id)
				if len(choices_id) > 0:
					response[question_id] = False
				else:
					number_of_correct_answers += 1
			else:
				return JsonResponse({"success": False, "question_not_found": f"Question with id={question_id} not found in this lesson"})

		total = number_of_correct_answers / len(test_questions_id) * 100

		response["total"] = total

		if total > 70:
			if not lesson.is_completed:
				lesson.is_completed = True
				lesson.save()

				if course.get_number_of_completed_lessons() == course.course.get_number_of_lessons():
					if course.has_final_test():
						if not course.is_completed:
							response["final_test_was_opened"] = True
					elif not course.is_completed:
						course.make_course_completed()
						response["course_was_completed"] = True
						response["course_has_certificate"] = course.course.has_certificate

		return JsonResponse(response)

	return JsonResponse({"success": False, "test_does_not_exist": "This lesson does not have a test"})


@token_auth_login_required
def get_forum_comments_view(request):
	if not (course_pk := int(request.GET.get("my_course_pk", False))):
		return JsonResponse({"success": False, "course_pk_not_found": "Course Primary Key Not Found"})
	if not (lesson_index := int(request.GET.get("lesson_index", False))):
		return JsonResponse({"success": False, "lesson_index_not_found": "Lesson Index Not Found"})
	startswith = int(request.GET.get("startswith", -1))
	if startswith == -1:
		return JsonResponse({"success": False, "startswith_not_found": "Starts with argument Not Found"})
	if not (endswith := int(request.GET.get("endswith", False))):
		return JsonResponse({"success": False, "endswith_not_found": "Ends with argument Not Found"})

	course = get_object_or_404(MyCourse, pk=course_pk, user_id=request.user.id)
	lessons = course.lessons.all()

	if len(lessons) >= lesson_index:
		lesson = lessons[lesson_index - 1]
	else:
		return JsonResponse({"lesson_not_found": "Lesson not found"})

	return get_comments(lesson, startswith, endswith)


@token_auth_login_required
def get_forum_nested_comments_view(request):
	if not (course_pk := int(request.GET.get("my_course_pk", False))):
		return JsonResponse({"success": False, "course_pk_not_found": "Course Primary Key Not Found"})
	if not (lesson_index := int(request.GET.get("lesson_index", False))):
		return JsonResponse({"success": False, "lesson_index_not_found": "Lesson Index Not Found"})
	startswith = int(request.GET.get("startswith", -1))
	if startswith == -1:
		return JsonResponse({"success": False, "startswith_not_found": "Starts with argument Not Found"})
	if not (endswith := int(request.GET.get("endswith", False))):
		return JsonResponse({"success": False, "endswith_not_found": "Ends with argument Not Found"})
	if not (parent_comment_id := int(request.GET.get("parent_comment_id", False))):
		return JsonResponse({"success": False, "parent_comment_not_found": "Parent comment Not Found"})

	course = get_object_or_404(MyCourse, pk=course_pk, user_id=request.user.id)
	lessons = course.lessons.all()

	if len(lessons) >= lesson_index:
		lesson = lessons[lesson_index - 1]
	else:
		return JsonResponse({"lesson_not_found": "Lesson not found"})

	return get_nested_comments(lesson, startswith, endswith, parent_comment_id)


@api_view(["POST"])
@token_auth_login_required
def ask_view(request):
	if not (course_pk := int(request.data.get("my_course_pk", 0))):
		return JsonResponse({"success": False, "course_pk_not_found": "Course Primary Key Not Found"})
	if not (lesson_index := int(request.data.get("lesson_index", 0))):
		return JsonResponse({"success": False, "lesson_index_not_found": "Lesson Index Not Found"})

	course = get_object_or_404(MyCourse, pk=course_pk, user_id=request.user.id)

	lessons = course.lessons.all()

	if len(lessons) >= lesson_index:
		lesson = lessons[lesson_index - 1]
	else:
		return JsonResponse({"success": False, "lesson_not_found": "Lesson not found"})

	form = ForumCommentForm(request.data)
	if form.is_valid():
		lesson.lesson.comments.create(user=request.user, comment=form.cleaned_data["comment"])
		return JsonResponse({"success": True})
	else:
		return JsonResponse({"success": False, "invalid_form_data": "The form is invalid"})


@api_view(["POST"])
@token_auth_login_required
def answer_view(request):
	if not (course_pk := int(request.data.get("my_course_pk", 0))):
		return JsonResponse({"success": False, "course_pk_not_found": "Course Primary Key Not Found"})
	if not (lesson_index := int(request.data.get("lesson_index", 0))):
		return JsonResponse({"success": False, "lesson_index_not_found": "Lesson Index Not Found"})

	course = get_object_or_404(MyCourse, pk=course_pk, user_id=request.user.id)

	lessons = course.lessons.all()

	if len(lessons) >= lesson_index:
		lesson = lessons[lesson_index - 1]
	else:
		return JsonResponse({"success": False, "lesson_not_found": "Lesson not found"})

	form = ForumCommentForm(request.data)
	if form.is_valid():
		parent_comment_id = int(request.data.get("parent_comment_id", 0))
		if parent_comment_id:
			parent_comment_id = int(parent_comment_id)
			comment = lesson.lesson.comments.filter(id=parent_comment_id)
			if comment:
				comment = comment[0]
				comment.nested_comments.create(user=request.user, comment=form.cleaned_data["comment"])
				return JsonResponse({"success": True})
			else:
				return JsonResponse({"success": False, "comment_not_found": f"There is no comment with id={parent_comment_id}"})
		else:
			return JsonResponse({"success": False, "invalid_form_data": "The form is invalid, you didn't put the parent_comment_id"})
	else:
		return JsonResponse({"success": False, "invalid_form_data": "The form is invalid"})


def am_i_authenticated_view(request):
	return JsonResponse({"you_are_authenticated": is_request_user_token_authenticated(request)})


@api_view(["POST"])
@ione_api_key_required
def token_auth_sign_up_view(request):
	response = token_auth_sign_up(request.data)
	return JsonResponse(response)


@api_view(["POST"])
@ione_api_key_required
def token_auth_login_view(request):
	response = token_auth_login(request.data)
	return JsonResponse(response)


@api_view(["POST"])
@token_auth_login_required
def token_auth_logout_view(request):
	response = token_auth_logout(request.user_token)
	return JsonResponse(response)


@api_view(["POST"])
@ione_api_key_required
def reset_password_view(request):
	form_data = json.dumps(request.data)
	response = auth_services.reset_password(form_data)
	return JsonResponse(response)


@ione_api_key_required
def get_course_categories_view(_):
	return JsonResponse({"success": True, "response": get_sections_tree()})


def get_course_view(request, course_pk):
	if is_request_user_token_authenticated(request):
		count = MyCourse.objects.filter(course_id=course_pk, user_id=request.user.id).count()
		user_already_has_course = True if count == 1 else False
		cashback_balance = request.user.cashback_balance
	elif is_request_user_authenticated_by_api_key(request):
		user_already_has_course = False
		cashback_balance = 0
	else:
		return JsonResponse({"invalid-api-key": "Invalid API-KEY"})

	course = get_course(course_pk)
	course[0]["fields"]["user_already_has_course"] = user_already_has_course
	course[0]["fields"]["user_cashback_balance"] = cashback_balance

	return JsonResponse({'success': True, 'response': course})


@ione_api_key_required
def get_course_feedbacks_view(request, course_pk):
	response = get_course_comments_in_range_from_0_to(endswith=int(request.GET.get("endswith", 10)), course_pk=course_pk)
	return JsonResponse({"success": True, "response": response})


@api_view(["POST"])
@token_auth_login_required
def get_access_to_course_by_coupon_view(request, course_pk):
	response = give_access_to_course_by_coupon(request.user, request.data, course_pk)
	return JsonResponse(response)


@ione_api_key_required
def get_section_view(_, section_pk):
	return JsonResponse({"success": True, "response": get_section(section_pk)})


@api_view(["POST"])
@token_auth_login_required
def add_to_fav_view(request, course_pk):
	request.user.favourite_courses.add(get_object_or_404(CompletedCourse, pk=course_pk))
	return JsonResponse({"success": True, "message": "Added successfully"})


@api_view(["POST"])
@token_auth_login_required
def remove_from_fav_view(request, course_pk):
	request.user.favourite_courses.remove(get_object_or_404(CompletedCourse, pk=course_pk))
	return JsonResponse({"success": True, "message": "Removed successfully"})


@token_auth_login_required
def profile_page_view(request):
	return JsonResponse({"success": True, "user": serialize("python", [request.user])})


@token_auth_login_required
def get_my_courses_view(request):
	return JsonResponse({"success": True, "my_courses": get_my_courses(request.user)})


@token_auth_login_required
def get_my_coupons_view(request):
	return JsonResponse({"success": True, "my_coupons": get_my_coupons(request.user)})


@token_auth_login_required
def get_my_certificates_view(request):
	return JsonResponse({"success": True, "my_certificates": get_my_certificates(request.user)})


@token_auth_login_required
def get_my_favourite_courses_view(request):
	courses = serialize("python", request.user.favourite_courses.all())
	_set_course_rating(courses)
	_set_course_authors(courses)
	return JsonResponse({"success": True, "my_favourite_courses": courses})


@api_view(["POST"])
@token_auth_login_required
def change_user_data_view(request):
	response = change_user_data(request.user, request.data)
	return JsonResponse(response)


@api_view(["POST"])
@token_auth_login_required
def change_password_view(request):
	response = change_user_password(request.user, request.data)
	return JsonResponse(response)


@api_view(["POST"])
@token_auth_login_required
def change_email_view(request):
	response = change_email(request.user, request.data)
	return JsonResponse(response)


@api_view(["POST"])
@token_auth_login_required
def view_coupon_view(request):
	response = get_coupon(request.user, request.data)
	return JsonResponse(response)


@token_auth_login_required
def get_my_course_view(request, my_course_pk):
	course = get_object_or_404(MyCourse, pk=my_course_pk, user_id=request.user.id)
	serialized_course = serialize("python", [course])
	serialized_course[0]["fields"]["course_video_url"] = course.course.video.url
	serialized_course[0]["fields"]["course_poster"] = course.course.poster.url
	serialized_course[0]["fields"]["course_title"] = course.course.title
	serialized_course[0]["fields"]["is_available"] = course.is_available()
	serialized_course[0]["fields"]["reached_course_percentage"] = course.get_course_passed_percentage()
	serialized_course[0]["fields"]["final_test_is_opened"] = False
	if course.get_number_of_completed_lessons() == course.course.get_number_of_lessons() and not course.is_completed:
		serialized_course[0]["fields"]["final_test_is_opened"] = True
	serialized_course[0]["fields"]["price_of_renew_access_for_two_weeks"] = course.get_price_for_renew_access(0.5)
	serialized_course[0]["fields"]["price_of_renew_access_for_one_month"] = course.get_price_for_renew_access(1)
	serialized_course[0]["fields"]["price_of_renew_access_for_two_months"] = course.get_price_for_renew_access(2)
	lessons = course.lessons.all()
	serialized_lessons = serialize("python", lessons)
	for i in range(len(serialized_lessons)):
		serialized_lessons[i]["fields"]["lesson_title"] = lessons[i].lesson.title
	return JsonResponse({"success": True, "my_course": serialized_course, "lessons": serialized_lessons})


@api_view(["POST"])
@token_auth_login_required
def leave_comment_view(request, my_course_pk):
	response = leave_course_comment(request.user, my_course_pk, request.data)
	return JsonResponse(response)


@token_auth_login_required
def get_lesson_view(request, lesson_index, my_course_pk):
	course = get_object_or_404(MyCourse, user_id=request.user.id, pk=my_course_pk)
	lessons = course.lessons.all()

	if len(lessons) >= lesson_index:
		lesson = lessons[lesson_index - 1]
	else:
		return JsonResponse({"success": False, "errors": {"404": "Page not found"}})

	try:
		test = lesson.lesson.test
		questions = list(test.questions.all())
		random.shuffle(questions)
	except ObjectDoesNotExist:
		test = None
		questions = None

	serialized_questions = serialize('python', questions)
	for i in range(len(serialized_questions)):
		choices = questions[i].choices.all()
		serialized_questions[i]["fields"]["answers_are_radio"] = True
		if choices.filter(is_answer=True).count() > 1:
			serialized_questions[i]["fields"]["answers_are_radio"] = False
		serialized_questions[i]["fields"]["answers"] = serialize("python", choices)

	return JsonResponse({
		"success": True,
		"lesson": serialize("python", [lesson.lesson]),
		"test": serialize('python', [test]),
		"questions": serialized_questions,
	})


@api_view(["POST"])
def get_courses_view(request, section_pk):
	response = get_courses(request.user, request.data, section_pk)
	if is_request_user_token_authenticated(request):
		_set_favourite_courses_among_serialized_courses(request.user.favourite_courses.all(), response["courses"])
	elif is_request_user_authenticated_by_api_key(request):
		_set_favourite_courses_among_serialized_courses(None, response["courses"])
	else:
		return JsonResponse({"invalid-api-key": 'Invalid API-KEY'})
	return JsonResponse({"success": True} | response)


@api_view(["POST"])
@token_auth_login_required
def get_access_to_free_course_view(request, course_pk):
	course = course_services.get_course(request.user, course_pk)
	return JsonResponse({"success": True, "course_pk": course.pk})


@api_view(["POST"])
@token_auth_login_required
def buy_course_view(request, course_pk):
	form = CoursePaymentForm(request.data)
	if form.is_valid():
		status, order = ioka_services.create_course_order(request.user, course_pk,
														  form.cleaned_data["payment_type"],
														  form.cleaned_data["use_cashback"])
		if status == 201:
			return JsonResponse({"success": True, "checkout_url": order["order"]["checkout_url"]})
		elif status == "Done":
			return JsonResponse({"success": True, "checkout_url": "Done"})

		return JsonResponse({"success": False, "ioka_create_order_error": order})
	return JsonResponse({"success": False, "errors": form.errors})
