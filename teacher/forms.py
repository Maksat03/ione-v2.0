from django import forms
from .models import PublishCourseRequest


class PublishCourseRequestForm(forms.ModelForm):
    class Meta:
        model = PublishCourseRequest
        fields = "__all__"
        widgets = {
            "teacher_phone_number": forms.TextInput({"placeholder": "Номер телефона", "class": "blocks"}),
            "teacher_first_name": forms.TextInput({"placeholder": "Имя", "class": "blocks"}),
            "teacher_last_name": forms.TextInput({"placeholder": "Фамилия", "class": "blocks"}),
            "teacher_course_direction": forms.TextInput({"placeholder": "Направление курса", "class": "blocks"}),
        }
