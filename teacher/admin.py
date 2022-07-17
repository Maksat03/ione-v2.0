from django.contrib import admin
from .models import Teacher, Achievement, Document, PublishCourseRequest

admin.site.register(Teacher)
admin.site.register(Achievement)
admin.site.register(Document)
admin.site.register(PublishCourseRequest)
