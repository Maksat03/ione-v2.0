from pathlib import Path
from typing import IO, Generator

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from courses.models import Comment
from courses.services import get_course_comments_in_range_from_0_to
from iOneLayer.services import user_is_using_ionelayer
from my_courses.forms import LeaveCommentForm, ForumCommentForm, RenewAccessForm
from my_courses.models import MyCourse

from ioka import services as ioka_services

import random


def my_course_page_view(request, course_pk):
	if not request.user.is_authenticated:
		return redirect("/courses/#log-zatemnenie")
	return render(request, "lessonsPage.html", {"my_course": get_object_or_404(MyCourse, user_id=request.user.id, pk=course_pk), "leave_comment_form": LeaveCommentForm(), "renew_access_form": RenewAccessForm()})


def leave_comment_view(request, course_pk):
	if not request.user.is_authenticated:
		return redirect("/courses/#log-zatemnenie")
	my_course = get_object_or_404(MyCourse, user_id=request.user.id, pk=course_pk)
	if my_course.is_available_until:
		if not my_course.is_available():
			print(reverse("my_course", kwargs={'course_pk': course_pk}))
			return redirect(reverse("my_course", kwargs={'course_pk': course_pk})+"#renew_access")

	if request.method == "POST":
		form = LeaveCommentForm(request.POST)
		if form.is_valid():
			Comment.objects.create(course=my_course.course.course, user=request.user, rating=int(form.cleaned_data["rating"]), comment=form.cleaned_data["comment"])
			ratings = Comment.objects.filter(course=my_course.course.course)
			rating = 0
			for r in ratings:
				rating += r.rating
			rating /= len(ratings)
			my_course.course.course.rating = round(rating, 1)
			my_course.course.course.save()
			return redirect(request.path[:request.path.index("leave_comment")])
		return HttpResponse("Form is invalid")
	return HttpResponse("You should send a request with 'POST' method")


def get_course_comments_view(request, course_pk):
	"""
	Этот контроллер используется в Lessons Page, чтобы получить
	список отзывов касательно определенному курсу(course_pk) из базы данных в диапазоне от 0 до request.GET["endswith"].
	"""
	if endswith := request.GET.get("endswith", None):
		my_course = get_object_or_404(MyCourse, user_id=request.user.id, pk=course_pk)
		response = get_course_comments_in_range_from_0_to(endswith=int(endswith), course_pk=my_course.course.pk)
		return JsonResponse({"success": True} | response)

	return JsonResponse({"success": False, "message": "You should send a GET request with 'endswith' key"})


def lesson_page_view(request, course_pk, lesson_index):
	if not request.user.is_authenticated:
		return redirect("/courses/#log-zatemnenie")
	course = get_object_or_404(MyCourse, user_id=request.user.id, pk=course_pk)
	if course.is_available_until:
		if not course.is_available():
			return redirect(reverse("my_course", kwargs={'course_pk': course_pk})+"#renew_access")

	if course.course.has_ionelayer_protection and (request.user_agent.is_mobile or request.user_agent.is_tablet):  # or request.user_agent.touch_capable:  # or request.user_agent.is_bot
		return render(request, "iOneLayerDownload.html")

	if course.course.has_ionelayer_protection and (not user_is_using_ionelayer(request) and not request.user.is_superuser):
		return render(request, "iOneLayerDownload.html")

	lessons = course.lessons.all()

	if len(lessons) >= lesson_index:
		lesson = lessons[lesson_index - 1]
	else:
		return Http404("Page not found")

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
			"course_pk": course_pk,
			"lesson_index": lesson_index,
			"lessons": lessons,
			"lesson": lesson,
			"test": test,
			"questions": questions,
			"number_of_comments": number_of_comments,
			"leave_comment_form": ForumCommentForm()
		}
	)


def ranged(file: IO[bytes], start: int = 0, end: int = None, block_size: int = 8192) -> Generator[bytes, None, None]:
	consumed = 0

	file.seek(start)
	while True:
		data_length = min(block_size, end - start - consumed) if end else block_size
		if data_length <= 0:
			break
		data = file.read(data_length)
		if not data:
			break
		consumed += data_length
		yield data

	if hasattr(file, 'close'):
		file.close()


def stream(lesson, _range):
	video = lesson.lesson.video

	path = Path(video.path)

	file = path.open('rb')
	file_size = path.stat().st_size

	content_length = file_size
	status_code = 200
	content_range = _range

	if content_range is not None:
		content_ranges = content_range.strip().lower().split('=')[-1]
		range_start, range_end, *_ = map(str.strip, (content_ranges + '-').split('-'))
		range_start = max(0, int(range_start)) if range_start else 0
		range_end = min(file_size - 1, int(range_end)) if range_end else file_size - 1
		content_length = (range_end - range_start) + 1
		file = ranged(file, start=range_start, end=range_end + 1)
		status_code = 206
		content_range = f'bytes {range_start}-{range_end}/{file_size}'

	# return file, status_code, content_length, content_range

	response = StreamingHttpResponse(file, status=status_code, content_type='video/mp4')

	response['Accept-Ranges'] = 'bytes'
	response['Content-Length'] = str(content_length)
	response['Cache-Control'] = 'no-cache'
	response['Content-Range'] = content_range

	return response


def stream_view(request, course_pk, lesson_index):

	# Гугл дискта видео тур осы нарсенын объяснение

	if not user_is_using_ionelayer(request) and not request.user.is_superuser:
		return HttpResponse("You must use iOneLayer in order to watch the video")

	if not request.META.get("HTTP_REFERER"):
		return HttpResponse("You can't download a video xD")

	course = get_object_or_404(MyCourse, user_id=request.user.id, pk=course_pk)
	lessons = course.lessons.all()

	if len(lessons) >= lesson_index:
		lesson = lessons[lesson_index - 1]
	else:
		return Http404("Page not found")

	return stream(lesson, request.headers.get('range'))


def check_user_is_using_ionelayer_view(request, course_pk=None, lesson_index=None):
	if request.user.is_authenticated:
		if not user_is_using_ionelayer(request) and not request.user.is_superuser:
			return HttpResponse("User is not using iOneLayer")
		return HttpResponse("User is using iOneLayer")
	return HttpResponse("You are not authenticated")


def renew_access_view(request, course_pk):
	if request.method == "POST" and request.user.is_authenticated:
		form = RenewAccessForm(request.POST)
		if form.is_valid():
			status, order = ioka_services.create_course_renew_access_order(request.user, course_pk, float(form.cleaned_data["months"]))
			if status == 201:
				return render(request, "ioka.html", {
					"order_id": order["order"]["id"], "order_access_token": order["order_access_token"],
					"order_description": order["order"]["description"]
				})
			return JsonResponse({"success": False, "ioka_create_order_error": order})
		return JsonResponse({"success": False, "errors": form.errors})
	return redirect(reverse("my_course", kwargs={"course_pk": course_pk}))
