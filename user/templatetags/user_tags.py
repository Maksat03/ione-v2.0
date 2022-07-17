from django import template
from user.forms import SignUpForm, LoginForm, ResetPasswordForm


register = template.Library()


@register.simple_tag(name="get_registration_form")
def get_registration_form():
    return SignUpForm()


@register.simple_tag(name="get_login_form")
def get_login_form():
    return LoginForm()


@register.simple_tag(name="get_reset_password_form")
def get_reset_password_form():
    return ResetPasswordForm()
