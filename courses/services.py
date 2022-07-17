from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.core.serializers import serialize
from django.contrib.auth.hashers import check_password

from courses.forms import CouponForm
from my_courses.models import MyCourse
from courses.models import Coupon, CompletedCourse
from sections.services import _set_course_authors, _set_course_rating, _set_favourite_courses_among_serialized_courses
from user.models import User


def get_course_comments_in_range_from_0_to(endswith, course_pk):
    course = get_object_or_404(CompletedCourse, pk=course_pk)
    comments = course.course.get_comments()

    if len(comments) <= endswith:
        no_more_comment = True
    else:
        no_more_comment = False

    serialized_comments_data = serialize("python", comments)
    serialized_comments_data = serialized_comments_data[-1:-endswith-1:-1]
    for i in serialized_comments_data:
        user = User.objects.get(pk=i["fields"]["user"])
        i["fields"]["user_photo"] = user.photo.url
        i["fields"]["username"] = user.first_name + " " + user.last_name

    for i in range(len(serialized_comments_data)):
        del serialized_comments_data[i]["pk"], serialized_comments_data[i]["model"], serialized_comments_data[i]["fields"]["course"], serialized_comments_data[i]["fields"]["user"]

    response = {
        "no_more_comment": no_more_comment,
        "comments": serialized_comments_data,
        "number_of_comments": len(comments)
    }

    return response


def get_user_coupons_in_n_x_3_matrix(user):
    coupons = Coupon.objects.filter(user_id=user.id)
    coupons_in_n_x_3_matrix = []

    for i, coupon in enumerate(coupons):
        if i % 3 == 0:
            coupons_in_n_x_3_matrix.append([])
        last_item_index = len(coupons_in_n_x_3_matrix) - 1
        coupons_in_n_x_3_matrix[last_item_index].append(coupon)

    return coupons_in_n_x_3_matrix


def get_user_courses_with_certificate_in_n_x_3_matrix(user):
    courses = MyCourse.objects.filter(user_id=user.id, is_completed=True, course__has_certificate=True)
    courses_with_certificate_in_n_x_3_matrix = []

    for i, course in enumerate(courses):
        if i % 3 == 0:
            courses_with_certificate_in_n_x_3_matrix.append([])
        last_item_index = len(courses_with_certificate_in_n_x_3_matrix) - 1
        courses_with_certificate_in_n_x_3_matrix[last_item_index].append(course)

    return courses_with_certificate_in_n_x_3_matrix


def get_coupon(user, form_data):
    password_is_correct = check_password(form_data["password"], user.password)
    if password_is_correct:
        coupon = get_object_or_404(Coupon, pk=form_data["coupon_pk"])
        if user == coupon.user:
            return {"success": True, "coupon_number": coupon.coupon}
        else:
            return {"success": False, "message": "You don't have an access to this coupon"}
    else:
        return {"success": False, "password_is_invalid": True, "message": "Password is invalid"}


def give_access_to_course_by_coupon(user, form_data, course_pk):
    form = CouponForm(form_data)
    if form.is_valid():
        coupon = get_object_or_404(Coupon, coupon=form.cleaned_data["coupon"], course_id=course_pk, is_active=False)
        coupon.is_active = True
        coupon.save()
        my_course = MyCourse.objects.create(user=user, course=coupon.course, is_available_until=datetime.today() + relativedelta(months=coupon.course.access_months))
        coupon.course.course.number_of_students += 1
        coupon.course.course.save()
        return {"success": True, "url": my_course.get_absolute_url()}
    else:
        return {"success": False, "errors": form.errors}


def get_searched_courses(user, search, endswith):
    print(search)
    courses = [course for course in CompletedCourse.objects.filter(title__icontains=search, is_last_edition=True)]
    [courses.append(course) for course in CompletedCourse.objects.filter(Q(authors__user_account__first_name__icontains=search) | Q(authors__user_account__last_name__icontains=search), is_last_edition=True)]
    [courses.append(course) for course in CompletedCourse.objects.filter(tags__name__icontains=search, is_last_edition=True)]
    courses = list(set(courses))

    if len(courses) <= endswith:
        no_more_course = True
    else:
        no_more_course = False

    courses = serialize("python", courses[:endswith])
    _set_course_authors(courses)
    _set_course_rating(courses)

    if user.is_authenticated:
        user_favourite_courses = user.favourite_courses.all()
        _set_favourite_courses_among_serialized_courses(user_favourite_courses, courses)

    for i in range(len(courses)):
        del courses[i]["model"], courses[i]["fields"]["created_at"], \
            courses[i]["fields"]["course"], \
            courses[i]["fields"]["language"], courses[i]["fields"]["has_homeworks"], \
            courses[i]["fields"]["has_subtitles"], \
            courses[i]["fields"]["has_certificate"], courses[i]["fields"][
            "about_course"], courses[i]["fields"]["video"], \
            courses[i]["fields"]["number_of_homeworks"], courses[i]["fields"][
            "access_months"], \
            courses[i]["fields"]["is_last_edition"], courses[i]["fields"]["cash_type"], \
            courses[i]["fields"]["commission"], \
            courses[i]["fields"]["proceeds_for_current_month"], courses[i]["fields"][
            "is_top"], \
            courses[i]["fields"]["sections"], courses[i]["fields"]["tags"]

        for j in range(len(courses[i]["fields"]["authors"])):
            del courses[i]["fields"]["authors"][j]["brief_about_author"], \
                courses[i]["fields"]["authors"][j]["img_url"]

    return no_more_course, courses


def get_course(user, course_pk):
    course = get_object_or_404(CompletedCourse, id=course_pk, is_free=True)
    course.course.number_of_students += 1
    course.course.save()
    return MyCourse.objects.create(user=user, course=course, is_available_until=datetime.today() + relativedelta(months=course.access_months))
