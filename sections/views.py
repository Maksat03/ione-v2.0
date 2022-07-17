import json

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Section
from . import services


def section_page_view(request, section_pk):
	section = get_object_or_404(Section, pk=section_pk)
	number_of_courses, number_of_students = services.get_number_of_courses_and_students_of_section(section)
	similar_sections = section.similar_sections.all()

	context_data = {
		"section": section,
		"number_of_courses": number_of_courses,
		"number_of_students": number_of_students,
		"similar_sections": similar_sections
	}

	return render(request, "sectionPage.html", context_data)


def get_courses_view(request, section_pk):
	if request.method == "POST" and request.is_ajax():
		response = services.get_courses(request.user, json.loads(request.body), section_pk)
		return JsonResponse({"success": True} | response)

	return JsonResponse({'success': False, 'message': 'You should send a request with "POST" method'})


def section_authors_view(request, section_pk):
	section = get_object_or_404(Section, pk=section_pk)
	if author_name := request.GET.get("search_author", ""):
		authors = services.search_author_in_section(author_name, section)
	else:
		authors = services.get_section_authors(section)
	return render(request, "authors.html", {"authors": authors, "search_author_name": author_name})


def author_add_to_favourite_view(request, section_pk, author_id):
	if request.method == "POST" and request.is_ajax() and request.user.is_authenticated:
		success = services.author_add_to_favourite(request.user, section_pk, author_id)
		return JsonResponse({"success": success})
	return JsonResponse({"success": False})


def author_remove_from_favourite_view(request, section_pk, author_id):
	if request.method == "POST" and request.is_ajax() and request.user.is_authenticated:
		success = services.author_remove_from_favourite(request.user, section_pk, author_id)
		return JsonResponse({"success": success})
	return JsonResponse({"success": False})
