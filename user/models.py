from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from .managers import UserManager


class User(AbstractUser):
	created_at = models.DateField(auto_now_add=True)
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	date_of_birth = models.DateField(blank=True, null=True)
	phone_number = PhoneNumberField()
	email = models.EmailField(_("email address"), unique=True)
	user_agreement = models.BooleanField(null=True)
	photo = models.ImageField(upload_to="user-photos/%Y/%m/%d/", default="user-photos/default.png")
	favourite_courses = models.ManyToManyField("courses.CompletedCourse", blank=True)
	favourite_authors = models.ManyToManyField("teacher.Teacher", blank=True)
	last_password_changing = models.DateField(blank=True, null=True)
	cashback_balance = models.FloatField(default=0)

	username = None
	USERNAME_FIELD = "email"
	REQUIRED_FIELDS = []

	objects = UserManager()

	def needs_to_give_completed_user_data(self):
		return False if self.phone_number and self.date_of_birth else True

	def get_user_courses(self):
		courses = self.my_courses.all()
		result = []

		for course in courses:
			result.append(course.course)

		return result
