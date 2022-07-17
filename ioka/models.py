from datetime import datetime
from django.db import models


class CourseOrder(models.Model):
    user = models.ForeignKey("user.User", on_delete=models.PROTECT, related_name="orders")
    course = models.ForeignKey("courses.CompletedCourse", on_delete=models.PROTECT, related_name="orders")
    payment_type = models.CharField(max_length=255)
    order_id = models.CharField(max_length=255)
    order_access_token = models.CharField(max_length=255)
    due_date = models.DateTimeField()
    is_paid = models.BooleanField(default=False)
    checkout_url = models.CharField(max_length=255)

    price = models.FloatField()
    income_for_ione = models.FloatField(default=0)
    customer_is_using_cashback = models.BooleanField(default=False)

    def payment_time_is_expired(self):
        return datetime.now().timestamp() > self.due_date.timestamp()


class CourseRenewAccessOrder(models.Model):
    user = models.ForeignKey("user.User", on_delete=models.PROTECT)
    course = models.ForeignKey("my_courses.MyCourse", on_delete=models.CASCADE)
    months = models.FloatField()
    order_id = models.CharField(max_length=255)
    order_access_token = models.CharField(max_length=255)
    due_date = models.DateTimeField()
    is_paid = models.BooleanField(default=False)
    checkout_url = models.CharField(max_length=255)

    price = models.FloatField()
    income_for_ione = models.FloatField(default=0)

    def payment_time_is_expired(self):
        return datetime.now().timestamp() > self.due_date.timestamp()
