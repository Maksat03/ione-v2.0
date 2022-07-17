from django.urls import path
from .views import *

urlpatterns = [
    path("", course_page_view, name="course"),
    path("trial-lesson/", trial_lesson_view, name="trial_lesson"),
    path("trial-lesson/stream/", trial_lesson_stream_view, name="trial_lesson_stream"),
    path("trial-lesson/forum/get_comments/", trial_lesson_get_comments_view),
    path("trial-lesson/forum/get_nested_comments/", trial_lesson_get_nested_comments_view),
    path("get_course/", get_course_view),
    path("buy/", course_buy_view),
    path("coupon/", course_coupon_view),  # ajax
    path("get_comments/", get_course_comments_view),  # ajax
    path("add_to_favourite/", add_to_favourite_view),  # ajax
    path("remove_from_favourite/", remove_from_favourite_view),  # ajax
    path("go_to_last_edition_course/", go_to_last_edition_course_view)
]
