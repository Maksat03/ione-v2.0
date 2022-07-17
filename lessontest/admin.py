from django.contrib import admin
from .models import *


admin.site.register(CompletedChoice)
admin.site.register(CompletedQuestion)
admin.site.register(CompletedTest)
admin.site.register(CompletedFinalTest)
admin.site.register(Choice)
admin.site.register(Question)
admin.site.register(Test)
admin.site.register(FinalTest)
