from threading import Thread

from django.contrib.auth import SESSION_KEY
from django.contrib.sessions.models import Session
from datetime import datetime

from django.contrib.auth.hashers import check_password
from django.core.mail import EmailMessage
from django.core.serializers import serialize
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

from courses.models import CompletedCourse, Coupon, Comment, TopCourse
from my_courses.forms import LeaveCommentForm
from my_courses.models import MyCourse
from project import settings
from sections.models import Section
from sections.services import _set_course_authors
from user.forms import LoginForm, SignUpForm, PasswordChangeForm
from user.models import User
from user.tokens import account_activation_token


def is_request_user_authenticated_by_api_key(request):
    authorization = request.META.get("HTTP_AUTHORIZATION", "")
    if authorization.startswith("API-KEY "):
        api_key = authorization.split()[1]
        if api_key == settings.IONE_API_KEY:
            return True
    return False


def ione_api_key_required(view):
    def check(*args, **kwargs):
        request = args[0]
        if is_request_user_authenticated_by_api_key(request):
            return view(*args, **kwargs)
        return JsonResponse({"success": False, "invalid-api-key": "Invalid API-KEY"})
    return check


def is_request_user_token_authenticated(request):
    authorization = request.META.get("HTTP_AUTHORIZATION", "")
    if authorization.startswith("Token "):
        token = authorization.split()[1]
        try:
            token = Token.objects.get(key=token)
            request.user = token.user
            request.user_token = token
            return True
        except ObjectDoesNotExist:
            pass
    return False


def token_auth_login_required(view):
    def check(*args, **kwargs):
        request = args[0]
        if is_request_user_token_authenticated(request):
            return view(*args, **kwargs)
        return JsonResponse({"success": False, "errors": {"unauthenticated": "User is not authenticated"}})
    return check


def token_auth_sign_up(auth_data):
    form = SignUpForm(auth_data)

    if form.is_valid():
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        message = render_to_string('acc_active_email.html', {
            'user': user,
            'domain': settings.DOMAIN_NAME,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        message = EmailMessage("iOne.education Account confirmation link", message, to=[user.email])
        Thread(target=message.send, daemon=True).start()

        return {"success": True}
    errors = form.errors.get_json_data()
    if errors.get('phone_number'):
        for i in range(len(errors["phone_number"])):
            if errors["phone_number"][i]["message"] == "Enter a valid phone number (e.g. +12125552368).":
                errors["phone_number"][i]["message"] = "Введите действительный номер телефона (например, +77081235467). Номер должен начинаться с +7"
                break
    return {"success": False, "errors": errors}


def token_auth_login(auth_data):
    form = LoginForm(None, auth_data)

    if form.is_valid():
        try:
            user = User.objects.get(email=form.cleaned_data["username"])
        except User.DoesNotExist:
            return {"success": False, "errors": {"404": "User not found"}}
        else:
            password_is_correct = check_password(form.cleaned_data["password"], user.password)

            if password_is_correct:
                token, created = Token.objects.get_or_create(user=user)
                if not created:
                    token.delete()
                    token.key = None
                    token.save()

                for session in Session.objects.all():
                    if int(session.get_decoded().get(SESSION_KEY)) == user.id:
                        session.delete()
                        break

                return {"success": True, "token": token.key}
            else:
                return {"success": False, "errors": {"password_does_not_match": "Пароль не совпадает"}}

    return {"success": False, "errors": form.error_messages}


def token_auth_logout(token):
    if token:
        try:
            Token.objects.get(key=token).delete()
            return {"success": True}
        except ObjectDoesNotExist:
            pass
    return {"success": False}


def get_course(course_pk):
    course = get_object_or_404(CompletedCourse, pk=course_pk)
    curriculum = list()
    for section in course.get_lessons_sections():
        curriculum.append({"section_title": section.title, "lessons": [lesson.title for lesson in section.get_lessons()]})
    course = serialize("python", [course])
    course[0]["fields"]["curriculum"] = curriculum
    _set_course_authors(course)
    return course


def get_section(section_pk):
    return serialize("python", [get_object_or_404(Section, pk=section_pk)])


def get_my_courses(user):
    courses = MyCourse.objects.filter(user_id=user.id)
    course_passed_percentages = list()
    for course in courses:
        course_passed_percentages.append(course.get_course_passed_percentage())
    courses = serialize("python", courses)
    for i in range(len(courses)):
        completed_course = CompletedCourse.objects.get(pk=courses[i]["fields"]["course"])
        courses[i]["fields"]["title"] = completed_course.title
        courses[i]["fields"]["poster"] = completed_course.poster.url
        courses[i]["fields"]["course_passed_percentage"] = course_passed_percentages[i]
        courses[i]["fields"]["authors"] = list()
        for author in completed_course.authors.all():
            courses[i]["fields"]["authors"].append(author.user_account.first_name + " " + author.user_account.last_name)
    return courses


def get_my_coupons(user):
    coupons = serialize("python", Coupon.objects.filter(user_id=user.id))
    for coupon in coupons:
        course = CompletedCourse.objects.get(pk=coupon["fields"]["course"])
        coupon["fields"]["course_title"] = course.title
        coupon["fields"]["course_price"] = course.current_price
    return coupons


def get_my_certificates(user):
    certificates = serialize("python", MyCourse.objects.filter(user_id=user.id, is_completed=True, course__has_certificate=True))
    for certificate in certificates:
        certificate["fields"]["course"] = serialize("python", [CompletedCourse.objects.get(pk=certificate["fields"]["course"])])
    return certificates


def change_user_password(user, request_data):
    form = PasswordChangeForm(user, request_data)
    if form.is_valid():
        user.last_password_changing = datetime.now()
        form.save()
        return {"success": True}
    return {"success": False, "errors": form.errors}


def leave_course_comment(user, my_course_pk, form_data):
    my_course = get_object_or_404(MyCourse, user_id=user.id, pk=my_course_pk)
    form = LeaveCommentForm(form_data)
    if form.is_valid():
        Comment.objects.create(course=my_course.course.course,
                               user=user,
                               rating=int(form.cleaned_data["rating"]), comment=form.cleaned_data["comment"])
        ratings = Comment.objects.filter(course=my_course.course.course)
        rating = 0
        for r in ratings:
            rating += r.rating
        rating /= len(ratings)
        my_course.course.course.rating = round(rating, 1)
        my_course.course.course.save()
        return {"success": True}
    return {"success": False, "errors": form.errors}
