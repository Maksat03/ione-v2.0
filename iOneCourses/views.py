from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from courses.models import TopCourse
from sections.models import Section
from teacher.models import Teacher


def main_page_view(request):
	return render(request, "mainPage.html", {"tops": TopCourse.objects.all(), "sections": Section.objects.all()})


def post_course_page_view(request):
	return render(request, "mainPage.html")


def about_ione_education_page(request):
	# return render(request, "landing_page.html")
	return redirect("/courses/")


def author_view(request):
	if not (author_pk := request.GET.get("author_id", None)):
		return HttpResponse("Author ID parameter not found")
	author = get_object_or_404(Teacher, pk=int(author_pk))
	return render(request, "authorPage.html", {"author": author})
