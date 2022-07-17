from django import forms


CHOICES = (
    ('5', ''),
    ('4', ''),
    ('3', ''),
    ('2', ''),
    ('1', '')
)
MONTH_CHOICES = (
    (0.5, "2 неделя"),
    (1, "1 Месяц"),
    (2, "2 Месяц"),
)


class LeaveCommentForm(forms.Form):
    comment = forms.CharField(max_length=2000, widget=forms.TextInput(attrs={"class": "input", "placeholder": "Оставить свой комментарий"}))
    rating = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(attrs={"class": "simple-rating__item", "name": "simple-rating"}))


class ForumCommentForm(forms.Form):
    comment = forms.CharField(max_length=10000, widget=forms.Textarea(attrs={"class": "input", "placeholder": "Оставить свой комментарий", "rows": "2"}))


class RenewAccessForm(forms.Form):
    months = forms.ChoiceField(choices=MONTH_CHOICES, widget=forms.RadioSelect())
