import json

import jwt
from django.contrib.auth.hashers import check_password
from threading import Thread

from django.shortcuts import render

from project import settings
from .forms import PasswordChangeForm, ChangeEmailForm, ResetPasswordForm
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from user.forms import SignUpForm, LoginForm, ChangeUserDataForm
from django.contrib.auth import login as auth_login, SESSION_KEY
from django.contrib.sessions.models import Session
from django.core.mail import EmailMessage

from user.models import User
from user.tokens import account_activation_token, change_email_token, reset_password_token

from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist


def create_new_user_and_login(request):
    fields = json.loads(request.body)
    form = SignUpForm(fields)

    if form.is_valid():
        user = form.save()
        auth_login(request, user)

        return {"success": True}
    return {"success": False, "errors": form.errors}


def logout_from_other_devices_and_login_only_this_user(request):
    fields = json.loads(request.body)
    form = LoginForm(request, fields)

    if form.is_valid():
        auth_login(request, form.get_user())

        for session in Session.objects.all():
            if session.get_decoded().get(SESSION_KEY) == request.session[SESSION_KEY]:
                session.delete()
                break

        try:
            token = Token.objects.get(user=request.user)
            token.delete()
        except ObjectDoesNotExist:
            pass

        return {"success": True}
    return {"success": False, "errors": {'invalid_login': 'Пожалуйста, введите правильные email и пароль.'}}


def change_user_data(user, post, files=None):
    form = ChangeUserDataForm(post, files)
    if form.is_valid():
        user.first_name = form.cleaned_data["first_name"]
        user.last_name = form.cleaned_data["last_name"]
        user.phone_number = form.cleaned_data["phone_number"]
        user.date_of_birth = form.cleaned_data["date_of_birth"]
        if files:
            user.photo = form.cleaned_data["photo"]
        user.save()
        return {"success": True}
    errors = form.errors.get_json_data()
    if errors.get('phone_number'):
        for i in range(len(errors["phone_number"])):
            if errors["phone_number"][i]["message"] == "Enter a valid phone number (e.g. +12125552368).":
                errors["phone_number"][i]["message"] = "Введите действительный номер телефона (например, +77081235467). Номер должен начинаться с +7"
                break
    return {"success": False, "errors": errors}


def create_new_user_and_send_confirmation_link(request):
    fields = json.loads(request.body)
    if fields.get("phone_number", False):
        fields["phone_number"] = "+7"+fields["phone_number"]
    form = SignUpForm(fields)

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


def acc_activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, "active.html")
    else:
        return HttpResponse('Activation link is invalid!')


def change_password(request):
    form = PasswordChangeForm(request.user, request.POST)

    if form.is_valid():
        form.save_and_update_session_auth_hash(request)
        return {"success": True}
    return {"success": False, "errors": form.errors}


def change_email(user, form_data):
    form = ChangeEmailForm(form_data)

    if form.is_valid():
        try:
            User.objects.get(email=form.cleaned_data["email"])
            return {"success": False, "errors": {'email': ["Пользователь с таким эл. почтой уже есть! Напишите другой эл почту"]}}
        except ObjectDoesNotExist:
            pass

        password_is_correct = check_password(form.cleaned_data["password"], user.password)
        if password_is_correct:
            email = jwt.encode({"email": form.cleaned_data["email"]}, settings.EMAIL_JWT_ENCODE_SECRET_KEY, algorithm="HS256")
            message = render_to_string('change_email.html', {
                'user': user,
                'domain': settings.DOMAIN_NAME,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': change_email_token.make_token(user),
                'email': email
            })
            message = EmailMessage("iOne.education change email confirmation link", message, to=[form.cleaned_data["email"]])
            Thread(target=message.send, daemon=True).start()
            return {"success": True}
        return {"success": False, "errors": {"password": ["Пароль не верен"]}}
    return {"success": False, "errors": form.errors}


def activate_changing_email(request, email, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and change_email_token.check_token(user, token):
        try:
            email = jwt.decode(email, settings.EMAIL_JWT_ENCODE_SECRET_KEY, algorithms=["HS256"])["email"]
        except (jwt.exceptions.InvalidSignatureError, jwt.exceptions.DecodeError):
            return HttpResponse("Invalid email token")
        try:
            User.objects.get(email=email)
            return HttpResponse("User already exists")
        except ObjectDoesNotExist:
            pass
        user.email = email
        user.save()
        return render(request, "active.html")
    else:
        return HttpResponse('Activation link is invalid!')


def reset_password(form_data):
    form = ResetPasswordForm(json.loads(form_data))
    if form.is_valid():
        try:
            user = User.objects.get(email=form.cleaned_data["reset_password_email_field"])
        except ObjectDoesNotExist:
            return {"success": False, "errors": {"user_does_not_exist": ["Пользователь с таким эл. почты не существует"]}}

        message = render_to_string("reset_password.html", {
            "user": user,
            "domain": settings.DOMAIN_NAME,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": reset_password_token.make_token(user),
            "email": form.cleaned_data["reset_password_email_field"]
        })
        message = EmailMessage("iOne.education reset password", message, to=[form.cleaned_data["reset_password_email_field"]])
        Thread(target=message.send, daemon=True).start()
        return {"success": True}
    return {"success": False, "errors": {"reset_password_email_field": ["Введите правильный email"]}}


def reset_password_activation(uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    return user, reset_password_token.check_token(user, token)
