from django.contrib import admin
from .models import Course, LessonsSection, Lesson, Comment,\
    Coupon, TopCourse, CompletedCourse, CompletedLessonsSection, \
    CompletedLesson, CourseTag, ProceedsHistory


admin.site.register(Course)
admin.site.register(LessonsSection)
admin.site.register(Lesson)
admin.site.register(CompletedCourse)
admin.site.register(CompletedLessonsSection)
admin.site.register(CompletedLesson)
admin.site.register(Comment)
admin.site.register(Coupon)
admin.site.register(TopCourse)
admin.site.register(CourseTag)
admin.site.register(ProceedsHistory)
