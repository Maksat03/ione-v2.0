from django.contrib import admin
from .models import Comment, NestedComment


admin.site.register(Comment)
admin.site.register(NestedComment)
