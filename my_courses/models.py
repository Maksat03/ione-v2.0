import os

from django.core.exceptions import ObjectDoesNotExist
from dateutil.relativedelta import relativedelta
from django.core.files import File
from django.urls import reverse
from django.db import models
from datetime import date, datetime
from project import settings
from PIL import Image, ImageDraw, ImageFont


class MyCourse(models.Model):
    created_at = models.DateField(auto_now_add=True)
    user = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name="my_courses")
    course = models.ForeignKey("courses.CompletedCourse", on_delete=models.PROTECT)
    is_available_until = models.DateField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    completed_date = models.DateField(null=True, blank=True)
    certificate = models.FileField(upload_to="certificates/%Y/%m/%d/", null=True, blank=True)

    def __str__(self):
        return self.course.title

    def save(self, *args, **kwargs):
        if not self.pk:  # object is not in db yet
            super(MyCourse, self).save(*args, **kwargs)
            for lesson in self.course.get_lessons():
                self.lessons.create(lesson=lesson)
        else:
            super(MyCourse, self).save(*args, **kwargs)

    def get_course_passed_percentage(self):
        return int(self.get_number_of_completed_lessons() / self.course.number_of_lessons * 100)

    def get_number_of_completed_lessons(self):
        return self.lessons.filter(is_completed=True).count()

    def is_available(self):
        return date.today() <= self.is_available_until

    def is_today_last_available_day(self):
        return date.today() == self.is_available_until

    def is_timeout(self):
        return date.today() > self.is_available_until

    def get_absolute_url(self):
        return reverse("my_course", kwargs={"course_pk": self.pk})

    def has_final_test(self):
        try:
            final_test = self.course.final_test
            return True
        except ObjectDoesNotExist:
            return False

    def make_certificate(self):
        img = Image.open(settings.MEDIA_ROOT / "certificates/default_certificate.png", mode='r')
        image_width = img.width
        image_height = img.height
        draw = ImageDraw.Draw(img)

        font = ImageFont.truetype(
            str(settings.MEDIA_ROOT / "certificates/certificate.ttf"),
            140
        )
        text_width, text_height = draw.textsize(self.user.first_name + " " + self.user.last_name, font=font)
        draw.text(
            (
                (image_width - text_width) / 2,
                ((image_height - text_height) / 2) + 40
            ),
            self.user.first_name + " " + self.user.last_name,
            font=font,
            fill="#00c1cd"
        )

        font = font.font_variant(size=75)
        text_width, text_height = draw.textsize(f"завершил курс «{self.course.title}»", font=font)
        draw.text(
            (
                ((image_width - text_width) / 2),
                ((image_height - text_height) / 2) + 205
            ),
            f"завершил курс «{self.course.title}»",
            font=font,
            fill=(0, 0, 0, 0)
        )

        font = font.font_variant(size=50)
        author = self.course.authors.all()[0]
        draw.text(
            (
                2200,
                2150
            ),
            author.user_account.first_name + " " + author.user_account.last_name,
            font=font,
            fill=(0, 0, 0, 0)
        )

        draw.text(
            (
                250,
                2150
            ),
            str(datetime.today().date()),
            font=font,
            fill=(0, 0, 0, 0)
        )

        draw.text(
            (
                825,
                2150
            ),
            "Ирисбеков М.Б",
            font=font,
            fill=(0, 0, 0, 0)
        )

        img_name = "{}.png".format(f"certificate_{self.pk}")
        img.save(img_name)
        return img_name

    def make_course_completed(self, *args, **kwargs):
        self.is_completed = True
        self.completed_date = datetime.now()
        if self.course.has_certificate:
            img = self.make_certificate()
            img_file = open(img, "rb")
            dj_file = File(img_file)
            dj_file.name = "certificate.png"
            self.certificate = dj_file
            self.save()
            img_file.close()
            os.remove(img_file.name)
        else:
            self.save()

    def renew_access(self, months, save=True):
        if months == 0.5:
            available_until = datetime.today() + relativedelta(days=14)
        else:
            available_until = datetime.today() + relativedelta(months=months)

        if self.is_available():
            rest_days = self.is_available_until - datetime.today().date()
            available_until += relativedelta(days=rest_days.days)

        if save:
            self.is_available_until = available_until
            self.save()
        else:
            return available_until

    def get_price_for_renew_access(self, months):
        if months == 0.5:
            price = (self.course.current_price / (self.course.access_months * 4)) * 2
        elif months == 1:
            price_for_month = (self.course.current_price / self.course.access_months)
            price = price_for_month - (price_for_month * (settings.RENEW_ACCESS_PERCENT_FOR_ONE_MONTHS / 100))
        else:  # months == 2
            price_for_month = (self.course.current_price / self.course.access_months)
            price = (price_for_month * 2) - ((price_for_month * 2) * (settings.RENEW_ACCESS_PERCENT_FOR_TWO_MONTHS / 100))
        price = int(price / 10) * 10
        return price

    def get_price_for_renew_access_for_half_month(self):
        return self.get_price_for_renew_access(0.5)

    def get_price_for_renew_access_for_month(self):
        return self.get_price_for_renew_access(1)

    def get_price_for_renew_access_for_two_months(self):
        return self.get_price_for_renew_access(2)


class Lesson(models.Model):
    my_course = models.ForeignKey(MyCourse, on_delete=models.CASCADE, related_name="lessons")
    lesson = models.ForeignKey("courses.CompletedLesson", on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
