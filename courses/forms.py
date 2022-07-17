from django import forms


CHOICES = (
    ('buy', 'Купить и продолжить сейчас'),
    ('get_coupon', 'Получить купон')
)


class CoursePaymentForm(forms.Form):
    payment_type = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)
    use_cashback = forms.BooleanField(required=False)


class CouponForm(forms.Form):
    coupon = forms.CharField(label="Введите номер купона:", max_length=10)
