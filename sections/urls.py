from django.urls import path, include
from .views import *

urlpatterns = [
    path("<int:section_pk>/", section_page_view, name="section"),
    path("<int:section_pk>/authors/", section_authors_view),
    path("<int:section_pk>/authors/add_to_favourite/<int:author_id>/", author_add_to_favourite_view),
    path("<int:section_pk>/authors/remove_from_favourite/<int:author_id>/", author_remove_from_favourite_view),
    path("<int:section_pk>/get_courses/", get_courses_view),  # ajax
    path("<int:section_pk>/course/<int:course_pk>/", include("courses.urls"))
]
