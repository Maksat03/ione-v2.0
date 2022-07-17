from datetime import datetime

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm, UserCreationForm, AuthenticationForm, PasswordChangeForm as AuthPasswordChangeForm
from django import forms
from .models import User


class SignUpForm(UserCreationForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Повторите пароль'}))
    user_agreement = forms.BooleanField(required=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "user_agreement", "phone_number")
        widgets = {
            "first_name": forms.TextInput({"placeholder": "Имя"}),
            "last_name": forms.TextInput({"placeholder": "Фамилия"}),
            "email": forms.EmailInput({"placeholder": "Email"}),
            "phone_number": forms.TextInput({"placeholder": "Тел. номер должен начинатся с +7"})
        }


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput({
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput({
           'class': 'form-control',
           'placeholder': 'Пароль'
        })
    )


class ChangeUserDataForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone_number", "date_of_birth", "photo")
        widgets = {
            "first_name": forms.TextInput({"placeholder": "Имя"}),
            "last_name": forms.TextInput({"placeholder": "Фамилия"}),
            "phone_number": forms.TextInput({"placeholder": "Ваш номер телефона"}),
            "date_of_birth": forms.DateInput({"placeholder": "Дата рождения"}),
            "photo": forms.FileInput()
        }


class PasswordChangeForm(AuthPasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({"placeholder": "Старый пароль"})
        self.fields['new_password1'].widget.attrs.update({"placeholder": "Новый пароль"})
        self.fields['new_password2'].widget.attrs.update({"placeholder": "Повтор новый пароль"})

    def save_and_update_session_auth_hash(self, request):
        self.user.last_password_changing = datetime.now()
        super(PasswordChangeForm, self).save()
        update_session_auth_hash(request, self.user)


class ChangeEmailForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput({'placeholder': 'Текущий пароль'})
    )
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput({'placeholder': 'Новый Email'})
    )


class ResetPasswordForm(forms.Form):
    reset_password_email_field = forms.EmailField(widget=forms.EmailInput({"placeholder": "Email"}))


class NewPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({"placeholder": "Новый пароль", "class": "blocks"})
        self.fields['new_password2'].widget.attrs.update({"placeholder": "Повтор новый пароль", "class": "blocks"})
