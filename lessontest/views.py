import json
import random
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from lessontest.models import CompletedChoice
from my_courses.models import MyCourse


def test_check_view(request, course_pk, lesson_index):
    if request.is_ajax() and request.method == "POST":
        course = get_object_or_404(MyCourse, user_id=request.user.id, pk=course_pk)
        lessons = course.lessons.all()

        if len(lessons) >= lesson_index:
            lesson = lessons[lesson_index - 1]
        else:
            return Http404("Page not found")

        try:
            test = lesson.lesson.test
        except ObjectDoesNotExist:
            test = None

        if test:
            request_data = json.loads(request.body)
            del request_data["csrfmiddlewaretoken"]
            test_questions_id = [question.id for question in test.questions.all()]

            response = {}
            number_of_correct_answers = 0

            for question_id in request_data.keys():
                question_id = int(question_id)
                if question_id in test_questions_id:
                    choices_id = [choice.id for choice in CompletedChoice.objects.filter(question_id=question_id, is_answer=True)]
                    response[question_id] = False
                    if len(choices_id) != len(request_data[str(question_id)]):
                        continue

                    for choice_id in request_data[str(question_id)]:
                        choice_id = int(choice_id)
                        if choice_id in choices_id:
                            response[question_id] = True
                            choices_id.remove(choice_id)
                    if len(choices_id) > 0:
                        response[question_id] = False
                    else:
                        number_of_correct_answers += 1
                else:
                    return Http404(f"Question with id={question_id} not found in this lesson")

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

        return HttpResponse("This lesson does not have a test")
    return HttpResponse("You should send an ajax request with 'post' method")


def final_test_view(request, course_pk):
    if not request.user.is_authenticated:
        return redirect("/courses/#log-zatemnenie")
    course = get_object_or_404(MyCourse, user_id=request.user.id, pk=course_pk)
    if course.has_final_test() and course.get_number_of_completed_lessons() == course.course.get_number_of_lessons():
        try:
            test = course.course.final_test
            questions = list(test.questions.all())
            random.shuffle(questions)
        except ObjectDoesNotExist:
            questions = None
        return render(
            request=request,
            template_name="fin-test.html",
            context={
                "course_title": course.course.title,
                "course_pk": course_pk,
                "questions": questions,
                "timer": course.course.final_test.time_limit_minutes
            }
        )
    else:
        return redirect(request.path.split("final_test")[0])


def check_final_test_view(request, course_pk):
    if request.is_ajax() and request.method == "POST":
        course = get_object_or_404(MyCourse, user_id=request.user.id, pk=course_pk)

        try:
            test = course.course.final_test
        except ObjectDoesNotExist:
            test = None

        if test:
            request_data = json.loads(request.body)
            del request_data["csrfmiddlewaretoken"]
            test_questions_id = [question.id for question in test.questions.all()]

            response = {}
            number_of_correct_answers = 0

            for question_id in request_data.keys():
                question_id = int(question_id)
                if question_id in test_questions_id:
                    choices_id = [choice.id for choice in
                                  CompletedChoice.objects.filter(question_id=question_id, is_answer=True)]
                    response[question_id] = False
                    if len(choices_id) != len(request_data[str(question_id)]):
                        continue

                    for choice_id in request_data[str(question_id)]:
                        choice_id = int(choice_id)
                        if choice_id in choices_id:
                            response[question_id] = True
                            choices_id.remove(choice_id)
                    if len(choices_id) > 0:
                        response[question_id] = False
                    else:
                        number_of_correct_answers += 1
                else:
                    return Http404(f"Question with id={question_id} not found in this lesson")

            total = number_of_correct_answers / len(test_questions_id) * 100

            response["total"] = total
            response["course_was_completed"] = False

            if total > 70:
                if not course.is_completed:
                    course.make_course_completed()
                    response["course_was_completed"] = True
                    response["course_has_certificate"] = course.course.has_certificate
                    if course.course.has_certificate:
                        response["certificate_url"] = course.certificate.url
            return JsonResponse(response)

        return HttpResponse("This course does not have a test")
    return HttpResponse("You should send an ajax request with 'post' method")
