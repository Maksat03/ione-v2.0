from django.urls import path, include

from ioka.views import ioka_payment_success_view
from .views import *
from courses.views import course_preview_view, course_search_view, course_search_api_view, remove_from_favourite_view, \
    add_to_favourite_view

urlpatterns = [
    path("", main_page_view, name="main"),
    path("course_preview/<int:course_pk>/", course_preview_view),
    path("user/", include("user.urls")),
    path("section/", include("sections.urls")),
    path("payment/success/<str:order_obj_id>/", ioka_payment_success_view),
    path("my_course/", include("my_courses.urls")),
    path("post_course/", post_course_page_view, name="post_course"),
    path("search/", course_search_view),
    path("search/course/<int:course_pk>/", include("courses.urls")),
    path("search-api/", course_search_api_view),
    path("authors/", author_view, name="authors"),
    path("authors/add_to_favourite/<int:course_pk>/", add_to_favourite_view),
    path("authors/remove_from_favourite/<int:course_pk>/", remove_from_favourite_view),
    path("api/", include("api.urls"))
]
