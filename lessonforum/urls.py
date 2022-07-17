from django.urls import path
from .views import *


urlpatterns = [
    path("get_comments/", get_comments_view),
    path("get_nested_comments/", get_nested_comments_view),
    path("leave_comment/", leave_comment_view),
    path("answer/", answer_view)
]
