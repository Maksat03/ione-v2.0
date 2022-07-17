from django.urls import path, include
from .views import *
from lessontest.views import final_test_view, check_final_test_view

urlpatterns = [
    path("", my_course_page_view, name="my_course"),
    path("renew_access/", renew_access_view),
    path("final_test/", final_test_view),
    path("final_test/test/check/", check_final_test_view),
    path("get_comments/", get_course_comments_view),
    path("leave_comment/", leave_comment_view),
    path("lesson/<int:lesson_index>/", lesson_page_view, name="lesson"),
    path("lesson/<int:lesson_index>/stream/", stream_view, name="stream"),
    path("lesson/<int:lesson_index>/check_user_is_using_ionelayer/", check_user_is_using_ionelayer_view),
    path("lesson/<int:lesson_index>/test/", include("lessontest.urls")),
    path("lesson/<int:lesson_index>/forum/", include("lessonforum.urls"))
]
