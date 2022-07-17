from django.core.serializers import serialize
from django.shortcuts import get_object_or_404

from courses.models import CompletedCourse
from django.db.models import Q

from sections.models import Section
from teacher.models import Teacher


def get_courses(user, request_data, section_pk):
	order_by = request_data["order_by"]
	filter_by = request_data["filter_by"]
	endswith = request_data["endswith"]

	if order_by == "course__number_of_students":
		courses = CompletedCourse.objects.filter(sections__pk=section_pk, is_last_edition=True).order_by("-is_top", order_by)
	else:
		courses = CompletedCourse.objects.filter(sections__pk=section_pk, is_last_edition=True).order_by(order_by)
	courses = _filter_courses(courses, filter_by)

	if len(courses) <= endswith:
		no_more_course = True
	else:
		no_more_course = False

	serialized_courses_data = serialize('python', courses[:endswith])

	if user.is_authenticated:
		user_favourite_courses = user.favourite_courses.all()
		_set_favourite_courses_among_serialized_courses(user_favourite_courses, serialized_courses_data)

	_set_course_authors(serialized_courses_data)
	_set_course_rating(serialized_courses_data)

	for i in range(len(serialized_courses_data)):
		del serialized_courses_data[i]["model"], serialized_courses_data[i]["fields"]["created_at"], serialized_courses_data[i]["fields"]["course"], \
			serialized_courses_data[i]["fields"]["language"], serialized_courses_data[i]["fields"]["has_homeworks"], serialized_courses_data[i]["fields"]["has_subtitles"], \
			serialized_courses_data[i]["fields"]["has_certificate"], serialized_courses_data[i]["fields"]["about_course"], serialized_courses_data[i]["fields"]["video"], \
			serialized_courses_data[i]["fields"]["number_of_homeworks"], serialized_courses_data[i]["fields"]["access_months"], \
			serialized_courses_data[i]["fields"]["is_last_edition"], serialized_courses_data[i]["fields"]["cash_type"], serialized_courses_data[i]["fields"]["commission"], \
			serialized_courses_data[i]["fields"]["proceeds_for_current_month"], serialized_courses_data[i]["fields"]["is_top"], \
			serialized_courses_data[i]["fields"]["sections"], serialized_courses_data[i]["fields"]["tags"]

		for j in range(len(serialized_courses_data[i]["fields"]["authors"])):
			del serialized_courses_data[i]["fields"]["authors"][j]["brief_about_author"], serialized_courses_data[i]["fields"]["authors"][j]["img_url"]

	response = {
		"no_more_course": no_more_course,
		"courses": serialized_courses_data
	}

	return response


def _filter_courses(courses, filter_by):
	for key in filter_by.keys():
		q = None

		for i in filter_by[key]["values_for_filtering"]:
			d = dict()
			d[key] = i

			if not q:
				q = Q(**d)
			else:
				q |= Q(**d)

		if q:
			courses = courses.filter(q)

	return courses


def _set_favourite_courses_among_serialized_courses(favourite_courses, serialized_courses):
	for serialized_course in serialized_courses:
		if not favourite_courses:
			serialized_course["fields"]["is_favourite"] = False
		else:
			is_favourite_course = favourite_courses.filter(pk=serialized_course['pk'])
			if is_favourite_course:
				serialized_course["fields"]["is_favourite"] = True
			else:
				serialized_course["fields"]["is_favourite"] = False


def get_number_of_courses_and_students_of_section(section):
	courses = CompletedCourse.objects.filter(sections__pk=section.pk)
	number_of_courses = len(courses)
	number_of_students = 0

	for course in courses:
		number_of_students += course.course.number_of_students

	return number_of_courses, number_of_students


def _set_course_authors(courses):
	for course in courses:
		for i in range(len(course["fields"]["authors"])):
			author_id = course["fields"]["authors"][i]
			author = Teacher.objects.get(id=author_id)
			course["fields"]["authors"][i] = {
				"name": f"{author.user_account.first_name} {author.user_account.last_name}",
				"url": f"/courses/authors/?author_id={author_id}",
				"brief_about_author": author.brief_about_author,
				"img_url": author.user_account.photo.url
			}


def _set_course_rating(courses):
	for course in courses:
		course['fields']['rating'] = CompletedCourse.objects.get(id=course['pk']).course.rating


def get_section_authors(section):
	courses = CompletedCourse.objects.filter(sections__pk=section.pk)
	authors = list()

	for course in courses:
		for author in course.authors.all():
			if author not in authors:
				authors.append(author)

	return authors


def search_author_in_section(author_name, section):
	courses = CompletedCourse.objects.filter(sections__pk=section.pk)
	courses = courses.filter(Q(authors__user_account__first_name=author_name) | Q(authors__user_account__last_name=author_name))
	if courses:
		result = list()
		for course in courses:
			for author in course.authors.all():
				if author.user_account.first_name == author_name or author.user_account.last_name == author_name:
					if author not in result:
						result.append(author)
		return result
	else:
		return None


def author_add_to_favourite(user, section_pk, author_id):
	section = get_object_or_404(Section, pk=section_pk)
	courses = CompletedCourse.objects.filter(sections__pk=section.pk, authors__id=author_id)
	if courses:
		author = Teacher.objects.get(id=author_id)
		user.favourite_authors.add(author)
		return True
	return False


def author_remove_from_favourite(user, section_pk, author_id):
	section = get_object_or_404(Section, pk=section_pk)
	courses = CompletedCourse.objects.filter(sections__pk=section.pk, authors__id=author_id)
	if courses:
		author = Teacher.objects.get(id=author_id)
		user.favourite_authors.remove(author)
		return True
	return False

