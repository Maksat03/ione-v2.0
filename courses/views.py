import random

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.urls import reverse

from lessonforum.views import get_comments, get_nested_comments
from my_courses.forms import ForumCommentForm
from my_courses.models import MyCourse
from my_courses.views import stream
from .forms import CoursePaymentForm, CouponForm
from .models import Course, CompletedCourse
from . import services
from ioka import services as ioka_services


def course_page_view(request, course_pk, section_pk=None):
	user_already_has_course = False
	my_course = None

	if request.user.is_authenticated:
		my_course = MyCourse.objects.filter(course_id=course_pk, user_id=request.user.id)
		if len(my_course) > 0:
			my_course = my_course[0]
			user_already_has_course = True

	return render(request, "aboutCourse.html", {"course": get_object_or_404(CompletedCourse, pk=course_pk), "payment_form": CoursePaymentForm(), "coupon_form": CouponForm(), "user_already_has_course": user_already_has_course, "my_course": my_course})


def go_to_last_edition_course_view(request, course_pk, section_pk=None):
	course = get_object_or_404(CompletedCourse, pk=course_pk)
	last_edition_course = get_object_or_404(CompletedCourse, course__pk=course.course.pk, is_last_edition=True)
	return redirect(last_edition_course)


def add_to_favourite_view(request, course_pk, section_pk=None):
	"""
	Функция добавляет курс(*course_pk) в request.user.favourite_courses если пользователь аутентифицирован
	"""
	if request.user.is_authenticated:
		request.user.favourite_courses.add(get_object_or_404(CompletedCourse, pk=course_pk))
		return JsonResponse({"success": True, "message": "Added successfully"})
	return JsonResponse({"success": False, "message": "User is not authenticated"})


def remove_from_favourite_view(request, course_pk, section_pk=None):
	"""
	Функция удаляет курс(*course_pk) из request.user.favourite_courses если пользователь аутентифицирован
	"""
	if request.user.is_authenticated:
		request.user.favourite_courses.remove(get_object_or_404(CompletedCourse, pk=course_pk))
		return JsonResponse({"success": True, "message": "Removed successfully"})
	return JsonResponse({"success": False, "message": "User is not authenticated"})


def course_buy_view(request, course_pk, section_pk=None):
	if hasattr(request.user, "teacher"):
		return redirect("/teacher/")
	if request.method == "POST" and request.user.is_authenticated:
		my_courses = MyCourse.objects.filter(course_id=course_pk, user_id=request.user.id)
		if len(my_courses) > 0:
			my_course = my_courses[0]
			return redirect(my_course.get_absolute_url())
		form = CoursePaymentForm(request.POST)
		if form.is_valid():
			status, order = ioka_services.create_course_order(request.user, course_pk, form.cleaned_data["payment_type"], form.cleaned_data["use_cashback"])
			if status == 201:
				return render(request, "ioka.html", {
					"order_id": order["order"]["id"], "order_access_token": order["order_access_token"],
					"order_description": order["order"]["description"]
				})
			elif status == "Done":
				if form.cleaned_data["payment_type"] == "buy":
					course = MyCourse.objects.get(course_id=course_pk, user_id=request.user.id)
					return redirect(reverse("my_course", kwargs={"course_pk": course.pk}))
				return redirect(reverse("profile"))
			return JsonResponse({"success": False, "ioka_create_order_error": order})
		return JsonResponse({"success": False, "errors": form.errors})
	return redirect("/courses/#log-zatemnenie")


def course_coupon_view(request, course_pk, section_pk=None):
	if hasattr(request.user, "teacher"):
		return redirect("/teacher/")
	if request.is_ajax() and request.method == "POST" and request.user.is_authenticated:
		my_courses = MyCourse.objects.filter(course_id=course_pk, user_id=request.user.id)
		if len(my_courses) > 0:
			my_course = my_courses[0]
			return redirect(my_course.get_absolute_url())
		response = services.give_access_to_course_by_coupon(request.user, request.POST, course_pk)
		return JsonResponse(response)
	return JsonResponse({"success": False, "message": "You should send an ajax request with 'POST' method"})


def get_course_comments_view(request, course_pk, section_pk=None):
	"""
	Этот контроллер используется в About Course Page, чтобы получить
	список отзывов касательно определенному курсу(course_pk) из базы данных в диапазоне от 0 до request.GET["endswith"].
	"""
	if endswith := request.GET.get("endswith", None):
		response = services.get_course_comments_in_range_from_0_to(endswith=int(endswith), course_pk=course_pk)
		return JsonResponse({"success": True} | response)

	return JsonResponse({"success": False, "message": "You should send a GET request with 'endswith' key"})


def view_coupon_view(request):
	if request.is_ajax() and request.method == "POST" and request.user.is_authenticated:
		response = services.get_coupon(request.user, request.POST)
		return JsonResponse(response)
	return JsonResponse({"success": False, "errors": {"unauthorized": ["You were logged in by another device so this device was unauthorized"]}})


def course_preview_view(request, course_pk):
	####################################################################################################################################
	####################################################################################################################################
	####################################################################################################################################
	####################################################################################################################################
	course = get_object_or_404(Course, pk=course_pk)
	if request.user.is_superuser:  # or request.user is a teacher maybe I need to add this one...
		return render(request, "coursePreview.html", {"course": course, "lessons": course.get_lessons()})
	else:
		return redirect("/")


class Object(object):
	pass


def trial_lesson_view(request, course_pk, section_pk=None):
	course = get_object_or_404(CompletedCourse, pk=course_pk)
	lessons = course.get_lessons()
	lesson = Object()
	lesson.lesson = lessons[0]

	for i in range(len(lessons)):
		temp = lessons[i]
		lessons[i] = Object()
		lessons[i].lesson = temp

	try:
		test = lesson.lesson.test
		questions = list(test.questions.all())
		random.shuffle(questions)
	except ObjectDoesNotExist:
		test = None
		questions = None

	number_of_comments = lesson.lesson.comments.count()

	return render(
		request=request,
		template_name="VideoPage.html",
		context={
			"is_trial_lesson": True,
			"course_pk": course_pk,
			"lesson_index": 1,
			"lessons": lessons,
			"lesson": lesson,
			"test": test,
			"questions": questions,
			"number_of_comments": number_of_comments,
			"leave_comment_form": ForumCommentForm()
		}
	)


def trial_lesson_stream_view(request, course_pk, section_pk=None):
	course = get_object_or_404(CompletedCourse, pk=course_pk)
	lesson = Object()
	lesson.lesson = course.get_lessons()[0]
	return stream(lesson, request.headers.get('range'))


def trial_lesson_get_comments_view(request, course_pk, section_pk=None):
	course = get_object_or_404(CompletedCourse, pk=course_pk)
	lesson = Object()
	lesson.lesson = course.get_lessons()[0]
	startswith = int(request.GET.get("startswith"))
	endswith = int(request.GET.get("endswith"))
	return get_comments(lesson, startswith, endswith)


def trial_lesson_get_nested_comments_view(request, course_pk, section_pk=None):
	course = get_object_or_404(CompletedCourse, pk=course_pk)
	lesson = Object()
	lesson.lesson = course.get_lessons()[0]
	startswith = int(request.GET.get("startswith"))
	endswith = int(request.GET.get("endswith"))
	parent_comment_id = int(request.GET.get("parent_comment_id"))
	return get_nested_comments(lesson, startswith, endswith, parent_comment_id)


def course_search_view(request):
	search = request.GET.get("search", None)
	if search:
		return render(request, "coursesList.html", {"search_input": search})
	return redirect("/courses/")


def course_search_api_view(request):
	search = request.GET.get("search", None)
	if search:
		endswith = int(request.GET.get("endswith", 10))
		no_more_course, courses = services.get_searched_courses(request.user, search, endswith)
		return JsonResponse({"courses": courses, "no_more_course": no_more_course})
	return redirect("/courses/")


def get_course_view(request, course_pk, section_pk=None):
	if hasattr(request.user, "teacher"):
		return redirect("/teacher/")
	if request.method == "POST" and request.user.is_authenticated:
		my_courses = MyCourse.objects.filter(course_id=course_pk, user_id=request.user.id)
		if len(my_courses) > 0:
			my_course = my_courses[0]
			return redirect(my_course.get_absolute_url())
		course = services.get_course(request.user, course_pk)
		return redirect(course.get_absolute_url())
	return redirect("/courses/#log-zatemnenie")
