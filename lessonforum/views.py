from django.core.serializers import serialize
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect

from lessonforum.models import NestedComment
from my_courses.forms import ForumCommentForm
from my_courses.models import MyCourse
from user.models import User


def get_comments(lesson, startswith, endswith):
    comments = serialize("python", lesson.lesson.comments.order_by("-id"))

    if len(comments) <= endswith:
        no_more_comment = True
    else:
        no_more_comment = False

    if startswith < len(comments):
        comments = comments[startswith:endswith]

        for comment in comments:
            user = User.objects.get(pk=comment["fields"]["user"])
            comment["fields"]["user"] = {
                "image": user.photo.url,
                "first_name": user.first_name,
                "last_name": user.last_name
            }
            comment["fields"]["comment"] = comment["fields"]["comment"].strip()
            comment["fields"]["comment"] = comment["fields"]["comment"].split("\n")
            comment["fields"]["comment"] = "<br>".join(comment["fields"]["comment"])
            nested_comments = serialize("python", NestedComment.objects.filter(parent_comment_id=comment["pk"]))
            if len(nested_comments) > 0:
                if len(nested_comments) <= 2:
                    no_more_nested_comment = True
                else:
                    no_more_nested_comment = False

                nested_comments = nested_comments[:2]

                for nested_comment in nested_comments:
                    user = User.objects.get(pk=nested_comment["fields"]["user"])
                    nested_comment["fields"]["user"] = {
                        "image": user.photo.url,
                        "first_name": user.first_name,
                        "last_name": user.last_name
                    }
                    nested_comment["fields"]["comment"] = nested_comment["fields"]["comment"].strip()
                    nested_comment["fields"]["comment"] = nested_comment["fields"]["comment"].split("\n")
                    nested_comment["fields"]["comment"] = "<br>".join(nested_comment["fields"]["comment"])
                comment["nested_comments"] = nested_comments
                comment["no_more_nested_comment"] = no_more_nested_comment
                comment["startswith"] = 2
                comment["endswith"] = 7

        return JsonResponse({"success": True, "comments": comments, "no_more_comment": no_more_comment})
    return JsonResponse({"success": False, "message": "There is no more comment"})


def get_comments_view(request, course_pk, lesson_index):
    if request.is_ajax() and request.method == "GET":
        course = get_object_or_404(MyCourse, pk=course_pk, user_id=request.user.id)
        startswith = int(request.GET.get("startswith"))
        endswith = int(request.GET.get("endswith"))

        lessons = course.lessons.all()

        if len(lessons) >= lesson_index:
            lesson = lessons[lesson_index - 1]
        else:
            return Http404("Page not found")

        return get_comments(lesson, startswith, endswith)
    return JsonResponse({"success": False, "message": "You should send a 'get' request"})


def get_nested_comments(lesson, startswith, endswith, parent_comment_id):
    parent_comment = lesson.lesson.comments.filter(id=parent_comment_id)
    if parent_comment:
        comments = serialize("python", parent_comment[0].nested_comments.all())

        if len(comments) <= endswith:
            no_more_comment = True
        else:
            no_more_comment = False

        if startswith < len(comments):
            comments = comments[startswith:endswith]
            for comment in comments:
                user = User.objects.get(pk=comment["fields"]["user"])
                comment["fields"]["user"] = {
                    "image": user.photo.url,
                    "first_name": user.first_name,
                    "last_name": user.last_name
                }
                comment["fields"]["comment"] = comment["fields"]["comment"].strip()
                comment["fields"]["comment"] = comment["fields"]["comment"].split("\n")
                comment["fields"]["comment"] = "<br>".join(comment["fields"]["comment"])
            return JsonResponse(
                {"success": True, "comments": comments, "startswith": endswith, "endswith": endswith + 5,
                 "no_more_comment": no_more_comment})
        return JsonResponse({"success": False, "message": "There is no more comment"})
    return JsonResponse({"success": False, "message": "There is no parent comment"})


def get_nested_comments_view(request, course_pk, lesson_index):
    if request.is_ajax() and request.method == "GET":
        course = get_object_or_404(MyCourse, pk=course_pk, user_id=request.user.id)
        parent_comment_id = int(request.GET.get("parent_comment_id"))
        startswith = int(request.GET.get("startswith"))
        endswith = int(request.GET.get("endswith"))

        lessons = course.lessons.all()

        if len(lessons) >= lesson_index:
            lesson = lessons[lesson_index - 1]
        else:
            return Http404("Page not found")

        return get_nested_comments(lesson, startswith, endswith, parent_comment_id)
    return JsonResponse({"success": False, "message": "You should send a 'get' request"})


def leave_comment_view(request, course_pk, lesson_index):
    if not request.user.is_authenticated:
        return redirect("/courses/#log-zatemnenie")
    if request.method == "POST":
        course = get_object_or_404(MyCourse, pk=course_pk, user_id=request.user.id)

        lessons = course.lessons.all()

        if len(lessons) >= lesson_index:
            lesson = lessons[lesson_index - 1]
        else:
            return Http404("Page not found")

        form = ForumCommentForm(request.POST)
        if form.is_valid():
            lesson.lesson.comments.create(user=request.user, comment=form.cleaned_data["comment"])
        else:
            return HttpResponse("The form is invalid")

    return redirect(request.path.split("forum/leave_comment/")[0] + "#comments")


def answer_view(request, course_pk, lesson_index):
    if request.method == "POST":
        course = get_object_or_404(MyCourse, pk=course_pk, user_id=request.user.id)

        lessons = course.lessons.all()

        if len(lessons) >= lesson_index:
            lesson = lessons[lesson_index - 1]
        else:
            return Http404("Page not found")

        form = ForumCommentForm(request.POST)
        if form.is_valid():
            parent_comment_id = request.POST.get("parent_comment_id", False)
            if parent_comment_id:
                parent_comment_id = int(parent_comment_id)
                comment = lesson.lesson.comments.filter(id=parent_comment_id)
                if comment:
                    comment = comment[0]
                    comment.nested_comments.create(user=request.user, comment=form.cleaned_data["comment"])
                else:
                    return HttpResponse(f"There is no comment with id={parent_comment_id}")
            else:
                return HttpResponse("The form is invalid, you didn't put the parent_comment_id")
        else:
            return HttpResponse("The form is invalid")

    return redirect(request.path.split("forum/answer/")[0] + "#comments")
