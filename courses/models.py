from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse

from lessontest.models import CompletedTest, CompletedQuestion, CompletedChoice, CompletedFinalTest, Test

languages = (
    (1, "Kazakh"),
    (2, "Russian")
)

CASH_TYPE = (
    (-1, "CASH-"),
    (+1, "CASH+")
)


class CompletedLesson(models.Model):
    course = models.ForeignKey("CompletedCourse", on_delete=models.CASCADE)
    section = models.ForeignKey("CompletedLessonsSection", on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    text = models.TextField(default="<h3>Текстовый вариант урока</h3>")
    video = models.FileField(upload_to="completed-lesson-videos/%Y/%m/%d/", null=True, default="lesson-videos/default.mp4", validators=[FileExtensionValidator(allowed_extensions=["mp4"])])
    poster = models.ImageField(upload_to="completed-lesson-video-posters/%Y/%m/%d/", default="lesson-video-posters/default.png")

    def __str__(self):
        return self.title


class CompletedLessonsSection(models.Model):
    course = models.ForeignKey("CompletedCourse", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

    def get_lessons(self):
        return CompletedLesson.objects.filter(section_id=self.id)


class CourseTag(models.Model):
    name = models.CharField(max_length=50)


class CompletedCourse(models.Model):
    created_at = models.DateField(auto_now_add=True)
    course = models.ForeignKey("Course", on_delete=models.PROTECT)
    sections = models.ManyToManyField("sections.Section", related_name="courses")
    title = models.CharField(max_length=150)
    description = models.TextField()
    authors = models.ManyToManyField("teacher.Teacher")
    number_of_lessons = models.IntegerField()
    video_duration = models.FloatField()
    is_free = models.BooleanField()
    current_price = models.FloatField(default=0.0)
    original_price = models.FloatField(default=0.0)
    language = models.IntegerField(choices=languages, default=1)
    has_homeworks = models.BooleanField(default=True)
    has_subtitles = models.BooleanField(default=False)
    has_certificate = models.BooleanField(default=True)
    about_course = models.TextField()
    video = models.FileField(upload_to="course-videos/%Y/%m/%d/")
    poster = models.ImageField(upload_to="course-video-posters/%Y/%m/%d/")
    number_of_homeworks = models.IntegerField()
    access_months = models.IntegerField(default=3)
    is_last_edition = models.BooleanField(default=True)
    tags = models.ManyToManyField(CourseTag, blank=True)
    cash_type = models.IntegerField(choices=CASH_TYPE, default=-1)
    commission = models.FloatField(default=7.9)
    proceeds_for_current_month = models.FloatField(default=0)
    is_top = models.BooleanField(default=False)
    has_ionelayer_protection = models.BooleanField(default=False)

    def __str__(self):
        return str(self.title) + " " + str(self.is_last_edition)

    def get_authors(self):
        return self.authors.all()

    def get_lessons_sections(self):
        return CompletedLessonsSection.objects.filter(course_id=self.id)

    def get_lessons(self):
        sections = self.get_lessons_sections()
        lessons = []

        for section in sections:
            for lesson in section.get_lessons():
                lessons.append(lesson)

        return lessons

    def get_absolute_url(self):
        first_section = self.sections.all()[0]
        return reverse("course", kwargs={"section_pk": first_section.pk, "course_pk": self.pk})

    def get_number_of_lessons(self):
        return CompletedLesson.objects.filter(course_id=self.id).count()


class Lesson(models.Model):
    created_at = models.DateField(auto_now_add=True)
    course = models.ForeignKey("Course", on_delete=models.CASCADE)
    section = models.ForeignKey("LessonsSection", on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    text = models.TextField(blank=True, null=True)
    video = models.FileField(upload_to="lesson-videos/%Y/%m/%d/", default="lesson-videos/default.mp4")
    poster = models.ImageField(upload_to="lesson-video-posters/%Y/%m/%d/", default="lesson-video-posters/default.png")

    def __str__(self):
        return self.title


class LessonsSection(models.Model):
    created_at = models.DateField(auto_now_add=True)
    course = models.ForeignKey("Course", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

    def get_lessons(self):
        return Lesson.objects.filter(section_id=self.id)


class Course(models.Model):
    created_at = models.DateField(auto_now_add=True)
    sections = models.ManyToManyField("sections.Section")
    title = models.CharField(max_length=150)
    description = models.TextField()
    authors = models.ManyToManyField("teacher.Teacher")
    rating = models.FloatField(default=0.0)
    number_of_lessons = models.IntegerField()
    video_duration = models.FloatField()
    is_free = models.BooleanField()
    current_price = models.FloatField(default=10000.0)
    original_price = models.FloatField(default=15000.0)
    language = models.IntegerField(choices=languages, default=1)
    has_homeworks = models.BooleanField(default=True)
    has_subtitles = models.BooleanField(default=False)
    has_certificate = models.BooleanField(default=True)
    about_course = models.TextField()
    video = models.FileField(upload_to="course-videos/%Y/%m/%d/")
    poster = models.ImageField(upload_to="course-video-posters/%Y/%m/%d/")
    number_of_students = models.IntegerField(default=30)
    number_of_homeworks = models.IntegerField()
    access_months = models.IntegerField(default=3)
    is_complete = models.BooleanField(default=False)
    edition_number = models.IntegerField(default=1)
    cash_type = models.IntegerField(choices=CASH_TYPE, default=-1)
    commission = models.FloatField(default=7.9)
    has_ionelayer_protection = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_number_of_comments(self):
        return self.get_comments().count()

    def get_comments(self):
        return Comment.objects.filter(course_id=self.id)

    def get_number_of_rating_full_stars(self):
        return int(self.rating)

    def rating_has_half_star(self):
        return True if self.rating - int(self.rating) >= 0.5 else False

    def get_number_of_rating_no_stars(self):
        return 5 - round(self.rating)

    def get_authors(self):
        return self.authors.all()

    def get_lessons_sections(self):
        return LessonsSection.objects.filter(course_id=self.id)

    def get_lessons(self):
        sections = self.get_lessons_sections()
        lessons = []

        for section in sections:
            for lesson in section.get_lessons():
                lessons.append(lesson)

        return lessons

    def save(self, *args, **kwargs):
        if self.is_complete and self.pk:
            self.is_complete = False
            self.edition_number += 1

            for course in CompletedCourse.objects.filter(course_id=self.id):
                course.is_last_edition = False
                course.save()

            fields = self.__dict__.copy()
            del fields['_state'], fields['id'], fields['rating'], fields['created_at'],\
                fields['number_of_students'], fields['is_complete'], fields['edition_number']
            completed_course = CompletedCourse.objects.create(course=self, is_last_edition=True, **fields)

            for section in self.sections.all():
                completed_course.sections.add(section)

            for author in self.authors.all():
                completed_course.authors.add(author)

            for section in self.get_lessons_sections():
                fields = section.__dict__.copy()
                del fields['_state'], fields['id'], fields['course_id'], fields["created_at"]
                fields['course'] = completed_course
                completed_section = CompletedLessonsSection.objects.create(**fields)

                for lesson in section.get_lessons():
                    fields = lesson.__dict__.copy()
                    del fields['_state'], fields['id'], fields['course_id'], fields['section_id'], fields["created_at"]
                    fields['course'] = completed_course
                    fields['section'] = completed_section
                    completed_lesson = CompletedLesson.objects.create(**fields)

                    try:
                        test = lesson.test
                    except ObjectDoesNotExist:
                        test = None

                    if test:
                        completed_test = CompletedTest.objects.create(lesson=completed_lesson)

                        for question in test.questions.all():
                            completed_question = CompletedQuestion.objects.create(question=question.question)
                            for choice in question.choices.all():
                                CompletedChoice.objects.create(question=completed_question, choice=choice.choice, is_answer=choice.is_answer)
                            completed_test.questions.add(completed_question)


                    ########################################## think about lesson forum ##########################################

            try:
                final_test = self.final_test
            except ObjectDoesNotExist:
                final_test = None

            if final_test:
                completed_final_test = CompletedFinalTest.objects.create(course=completed_course, time_limit_minutes=final_test.time_limit_minutes)
                all_tests = Test.objects.filter(lesson__course_id=self.id)
                final_test_questions = final_test.questions.all()
                intersection = []

                for test in all_tests:
                    for question in test.questions.all():
                        if question in final_test_questions:
                            completed_final_test.questions.add(CompletedQuestion.objects.filter(question=question.question)[0])
                            intersection.append(question)

                non_intersection = [question for question in final_test_questions if question not in intersection]

                for question in non_intersection:
                    completed_question = CompletedQuestion.objects.create(question=question.question)
                    for choice in question.choices.all():
                        CompletedChoice.objects.create(question=completed_question, choice=choice.choice,
                                                       is_answer=choice.is_answer)
                    completed_final_test.questions.add(completed_question)

        super(Course, self).save(*args, **kwargs)


class Comment(models.Model):
    course = models.ForeignKey("Course", on_delete=models.CASCADE, related_name="feedbacks")
    user = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name='commenter')
    rating = models.IntegerField()
    time = models.DateField(auto_now_add=True)
    comment = models.TextField()


class Coupon(models.Model):
    created_at = models.DateField(auto_now_add=True)
    user = models.ForeignKey('user.User', on_delete=models.CASCADE)
    course = models.ForeignKey(CompletedCourse, on_delete=models.PROTECT)
    coupon = models.CharField(max_length=10)
    is_active = models.BooleanField(default=False)


class TopCourse(models.Model):
    section = models.ForeignKey("sections.Section", on_delete=models.CASCADE)
    courses = models.ManyToManyField(CompletedCourse)


class ProceedsHistory(models.Model):
    course = models.ForeignKey(CompletedCourse, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    proceeds = models.FloatField()
