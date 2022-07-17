from datetime import datetime

from django.core.serializers import serialize
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from courses.models import ProceedsHistory
from lessonforum.models import Comment, NestedComment
from teacher.forms import PublishCourseRequestForm
from teacher.models import Document
from teacher.services import load_nested_messages_of_forum, load_parent_messages_of_forum
from user.forms import PasswordChangeForm
from user.models import User


def teacher_page_view(request):
    if not hasattr(request.user, "teacher"):
        return redirect("/courses/")
    courses = request.user.teacher.get_courses()
    proceeds_for_current_month = 0
    proceeds_for_whole_months = 0
    proceeds = dict()
    history = dict()
    for course in courses:
        proceeds_for_current_month += course.proceeds_for_current_month
        proceeds[course.title] = course.proceeds_for_current_month

        for proceeds_history in ProceedsHistory.objects.filter(course_id=course.id):
            proceeds_for_whole_months += proceeds_history.proceeds
            history[proceeds_history.date] = history.get(proceeds_history.date, 0) + proceeds_history.proceeds
    return render(request, "teacherPage.html", {"proceeds_for_current_month": proceeds_for_current_month,
                                                "proceeds_for_whole_months": proceeds_for_whole_months,
                                                "proceeds": proceeds, "history": history, "courses": courses,
                                                "change_password_form": PasswordChangeForm(request.user)})


def subscribe_document_view(request, pk):
    document = get_object_or_404(Document, teacher=request.user.teacher, pk=pk)
    document.status = "answered"
    document.subscription_date = datetime.now()
    document.save()
    return redirect("/teacher/")


def refuse_document_view(request, pk):
    document = get_object_or_404(Document, teacher=request.user.teacher, pk=pk)
    document.status = "not_answered"
    document.subscription_date = datetime.now()
    document.save()
    return redirect("/teacher/")


def load_messages_of_forum_view(request):
    lesson_id = int(request.GET.get("lesson_id", 0))
    startswith = int(request.GET.get("startswith", 0))
    endswith = int(request.GET.get("endswith", 0))
    comments, no_more_messages = load_parent_messages_of_forum(lesson_id, startswith, endswith)

    comments = serialize("python", comments)
    for comment in comments:
        user = User.objects.get(id=comment["fields"]["user"])
        comment["fields"]["user"] = f"{user.first_name} {user.last_name}"
        comment["fields"]["user_img"] = user.photo.url
        comment["nested_comments"], comment["no_more_nested_messages"] = load_nested_messages_of_forum(comment["pk"], 0, 5)
        comment["nested_comments"] = serialize("python", comment["nested_comments"])

        for nested_comment in comment["nested_comments"]:
            user = User.objects.get(id=nested_comment["fields"]["user"])
            nested_comment["fields"]["user"] = f"{user.first_name} {user.last_name}"
            nested_comment["fields"]["user_img"] = user.photo.url

    return JsonResponse({"messages": comments, "no_more_messages": no_more_messages, "startswith": endswith, "endswith": endswith + 20})


def load_nested_messages_of_forum_view(request):
    parent_message_id = int(request.GET.get("parent_message_id", 0))
    startswith = int(request.GET.get("startswith", 0))
    endswith = int(request.GET.get("endswith", 0))
    comments, no_more_messages = load_nested_messages_of_forum(parent_message_id, startswith, endswith)

    comments = serialize("python", comments)
    for comment in comments:
        user = User.objects.get(id=comment["fields"]["user"])
        comment["fields"]["user"] = f"{user.first_name} {user.last_name}"
        comment["fields"]["user_img"] = user.photo.url

    return JsonResponse({"messages": comments, "no_more_nested_messages": no_more_messages, "startswith": endswith, "endswith": endswith + 5})


def leave_message_view(request):
    lesson_id = int(request.POST.get("lesson_id", 0))
    parent_message_id = int(request.POST.get(f"parent_comment_id", 0))
    nested_message_id = int(request.POST.get(f"nested_comment_id", 0))
    message = request.POST.get("message", "")

    if not parent_message_id:
        Comment.objects.create(user=request.user, lesson_id=lesson_id, comment=message)
    else:
        if nested_message_id:
            nested_message = NestedComment.objects.get(id=nested_message_id)
            message = f"{nested_message.user.first_name} {nested_message.user.last_name}, {message}"
        NestedComment.objects.create(user=request.user, parent_comment_id=parent_message_id, comment=message)

    return redirect("/teacher/")


def publish_course_request_view(request):
    form = PublishCourseRequestForm(request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "errors": form.errors})
