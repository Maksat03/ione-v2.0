from django.urls import path
from .views import test_check_view

urlpatterns = [
    path("check/", test_check_view),
]