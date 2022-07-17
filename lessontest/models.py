import random

from django.db import models


class CompletedChoice(models.Model):
    question = models.ForeignKey("CompletedQuestion", on_delete=models.CASCADE, related_name="choices")
    choice = models.TextField()
    is_answer = models.BooleanField(default=False)

    def __str__(self):
        return self.choice


class CompletedQuestion(models.Model):
    question = models.TextField()

    def __str__(self):
        return self.question

    def has_only_one_correct_answer(self):
        if CompletedChoice.objects.filter(question_id=self.id, is_answer=True).count() > 1:
            return False
        return True

    def get_choices(self):
        choices = list(self.choices.all())
        random.shuffle(choices)
        return choices


class CompletedTest(models.Model):
    lesson = models.OneToOneField("courses.CompletedLesson", on_delete=models.CASCADE, related_name="test")
    questions = models.ManyToManyField(CompletedQuestion)

    def __str__(self):
        return self.lesson.title


class CompletedFinalTest(models.Model):
    course = models.OneToOneField("courses.CompletedCourse", on_delete=models.CASCADE, related_name="final_test")
    questions = models.ManyToManyField(CompletedQuestion)
    time_limit_minutes = models.IntegerField()


class Choice(models.Model):
    question = models.ForeignKey("Question", on_delete=models.CASCADE, related_name="choices")
    choice = models.TextField()
    is_answer = models.BooleanField(default=False)

    def __str__(self):
        return self.choice


class Question(models.Model):
    question = models.TextField()

    def __str__(self):
        return self.question


class Test(models.Model):
    lesson = models.OneToOneField("courses.Lesson", on_delete=models.CASCADE, related_name="test")
    questions = models.ManyToManyField(Question)

    def __str__(self):
        return self.lesson.title


class FinalTest(models.Model):
    course = models.OneToOneField("courses.Course", on_delete=models.CASCADE, related_name="final_test")
    questions = models.ManyToManyField(Question)
    time_limit_minutes = models.IntegerField(default=30)
