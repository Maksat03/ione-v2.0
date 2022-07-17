from django.db import models
from courses.models import CompletedCourse
from phonenumber_field.modelfields import PhoneNumberField


class Teacher(models.Model):
    user_account = models.OneToOneField("user.User", on_delete=models.PROTECT, related_name="teacher")
    profession = models.CharField(max_length=150)
    about_author = models.TextField()
    brief_about_author = models.TextField()

    def __str__(self):
        return f"{self.user_account.first_name} {self.user_account.last_name}"

    def get_number_of_students(self):
        courses = self.get_courses()
        students = 0
        for course in courses:
            students += course.course.number_of_students

        return students

    def get_number_of_courses(self):
        return len(self.get_courses())

    def get_courses(self):
        return CompletedCourse.objects.filter(authors__pk=self.pk, is_last_edition=True)

    def get_rating(self):
        courses = self.get_courses()
        if not courses:
            return 0
        rating = 0

        for course in courses:
            rating += course.course.rating

        rating /= len(courses)
        return rating

    def get_number_of_rating_full_stars(self):
        return int(self.get_rating())

    def rating_has_half_star(self):
        rating = self.get_rating()
        return True if rating - int(rating) >= 0.5 else False

    def get_number_of_rating_no_stars(self):
        return 5 - round(self.get_rating())

    def get_diplomas(self):
        achievements = Achievement.objects.filter(achiever_id=self.pk)
        return achievements


class Achievement(models.Model):
    achiever = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="achievements/%Y/%m/%d/")


DOCS_TYPE = (
    ("contract", "Договор"),
    ("report", "Отчёт")
)

DOCS_STATUS_TYPE = (
    ("answered", "Подписано"),
    ("not_answered", "Отказано"),
    ("is_waiting", "В ожидании")
)


class Document(models.Model):
    file = models.FileField(upload_to="documents/%Y/%m/%d/")
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT, related_name="documents")
    title = models.CharField(max_length=255)
    created_at = models.DateField(auto_now_add=True)
    status = models.CharField(choices=DOCS_STATUS_TYPE, default="is_waiting", max_length=255)
    subscription_date = models.DateField(blank=True, null=True)
    docs_type = models.CharField(choices=DOCS_TYPE, default="Договор", max_length=255)


class PublishCourseRequest(models.Model):
    teacher_phone_number = PhoneNumberField()
    teacher_first_name = models.CharField(max_length=255)
    teacher_last_name = models.CharField(max_length=255)
    teacher_course_direction = models.CharField(max_length=500)

    def __str__(self):
        return self.teacher_course_direction
