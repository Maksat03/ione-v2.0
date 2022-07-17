from django.contrib import admin

from my_courses.models import MyCourse, Lesson

admin.site.register(MyCourse)
admin.site.register(Lesson)
