from django.urls import path, include
from .views import *
from courses import views as courses_views


urlpatterns = [
    path("login/", login_view),
    path("sign-up/", sign_up_view),
    path("profile/", profile_page_view, name="profile"),
    path("activate/<slug:uidb64>/<slug:token>/", activate, name='activate'),
    path("change_email_to/<str:email>/<slug:uidb64>/<slug:token>/", activate_changing_email_view, name='change_email'),

    path("profile/change_user_data/", change_user_data_view),

    path("profile/course/<int:course_pk>/", include("courses.urls")),
    path("profile/my_course/<int:course_pk>/", include("my_courses.urls")),
    path("profile/view_coupon/", courses_views.view_coupon_view),

    path("profile/change-password/", change_password_view),
    path("profile/change-email/", change_email_view),

    path("reset_password/", reset_password_view),
    path("reset_password_to/<slug:uidb64>/<slug:token>/", reset_password_to_view, name="reset_password"),

    path("", include('django.contrib.auth.urls'))
]
