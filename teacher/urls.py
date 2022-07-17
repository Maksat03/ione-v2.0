from django.urls import path

from user.views import change_password_view
from .views import teacher_page_view, refuse_document_view, subscribe_document_view, load_messages_of_forum_view, \
    load_nested_messages_of_forum_view, leave_message_view, publish_course_request_view

urlpatterns = [
    path("", teacher_page_view, name="teacher_page"),
    path("change-password/", change_password_view),
    path("subscribe_document/<int:pk>/", subscribe_document_view, name="subscribe_document"),
    path("refuse_document/<int:pk>/", refuse_document_view, name="refuse_document"),
    path("load_messages_of_forum/", load_messages_of_forum_view),
    path("load_nested_messages_of_forum/", load_nested_messages_of_forum_view),
    path("leave_message/", leave_message_view),
    path("publish_course_request/", publish_course_request_view)
]
