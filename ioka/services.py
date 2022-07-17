import base64
import os
from threading import Thread

import jwt
import pytz
import requests
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from django.core.mail import EmailMessage
from django.urls import reverse
from django.utils.timezone import make_aware

from my_courses.models import MyCourse
from project import settings
from django.shortcuts import get_object_or_404

from ioka.models import CourseOrder, CourseRenewAccessOrder
from courses.models import CompletedCourse, Coupon


def _create_order(order_data):
    response = requests.post(settings.IOKA_CREATE_ORDER_URL, headers=settings.IOKA_REQUEST_HEADER, json=order_data)
    return response.status_code, response.json()


def _create_order_data(price, due_date, jwt_order_id, order):
    order_data = {
        "amount": price*100,
        "currency": "KZT",
        "capture_method": "AUTO",
        "due_date": due_date.isoformat(),
        "success_url": settings.IOKA_PAYMENT_SUCCESS_URL + f"{jwt_order_id}/?order={order}",
        "back_url": settings.DOMAIN_NAME + reverse("profile")
    }
    return order_data


def create_course_order(user, course_pk, payment_type, use_cashback):
    course = get_object_or_404(CompletedCourse, pk=course_pk)
    due_date = datetime.now() + timedelta(days=1)
    price = course.current_price
    order_obj = CourseOrder.objects.create(price=price, user=user, course=course, payment_type=payment_type, due_date=make_aware(due_date, pytz.UTC))

    if use_cashback:
        order_obj.customer_is_using_cashback = True
        order_obj.save()

        if user.cashback_balance < price:
            price -= user.cashback_balance
            order_obj.price = price
            order_obj.save()
        else:
            order_obj.price = 0
            order_obj.save()
            success_course_order_payment(order_obj.id)
            return "Done", None

    jwt_order_id = jwt.encode({"order_obj_id": order_obj.id}, settings.ORDER_OBJ_ID_JWT_KEY, algorithm="HS256")
    order_data = _create_order_data(price, due_date, jwt_order_id, "course_order")

    if payment_type == "get_coupon":
        order_data["description"] = f'Услуга №{order_obj.id}. Получить купон к Курсу: {course.title}'
    else:
        order_data["description"] = f'Услуга №{order_obj.id}. Купить Курс: {course.title}'

    status, order = _create_order(order_data)

    if status == 201:
        order_obj.order_id = order["order"]["id"]
        order_obj.order_access_token = order["order_access_token"]
        order_obj.checkout_url = order["order"]["checkout_url"]
        order_obj.save()
    else:
        order_obj.delete()

    return status, order


def create_course_renew_access_order(user, course_pk, months):
    course = get_object_or_404(MyCourse, pk=course_pk, user_id=user.id)
    due_date = datetime.now() + timedelta(days=1)
    price = course.get_price_for_renew_access(months)
    order_obj = CourseRenewAccessOrder.objects.create(user=user, course=course, months=months, due_date=make_aware(due_date, pytz.UTC), price=price)
    jwt_order_id = jwt.encode({"order_obj_id": order_obj.id}, settings.ORDER_OBJ_ID_JWT_KEY, algorithm="HS256")

    order_data = _create_order_data(price, due_date, jwt_order_id, "course_renew_access_order")
    order_data["description"] = f'Услуга №{order_obj.id}. Продлить доступ к Курсу: {course.course.title}. До: {course.renew_access(months, save=False).date()}'
    status, order = _create_order(order_data)

    if status == 201:
        order_obj.order_id = order["order"]["id"]
        order_obj.order_access_token = order["order_access_token"]
        order_obj.checkout_url = order["order"]["checkout_url"]
        order_obj.save()
    else:
        order_obj.delete()

    return status, order


def success_course_order_payment(order_id):
    order = get_object_or_404(CourseOrder, id=order_id)
    if not order.is_paid and not order.payment_time_is_expired():
        if order.customer_is_using_cashback:
            cashback_is_been_using = order.course.current_price - order.price
            if cashback_is_been_using > order.user.cashback_balance:  # Send email to us in order to know who wanted to lie our system and get course using not true cashback
                message = f"""
                            User: {order.user.first_name} {order.user.last_name} with {order.user.id} ID, tried to get a course with not true cashback in {order.id}th CourseOrder.
                            """
                message = EmailMessage("iOne.education a user tried to buy 2 or more course by one exact cashback",
                                       message,
                                       to=[settings.EMAIL_HOST_USER])
                Thread(target=message.send, daemon=True).start()
                order.user.is_active = False
                order.user.save()
                return "<style>body { text-align: center; color: red; background-color: black}</style>Наша система зафиксировала вашу действие, вы попытались купить 2 или больше курса за неактивный счет кэшбека, мы с вами свяжемся, а пока вы в черном списке, ваш аккаунт неактивен. Если вы хотите с нами свяжется, вот наши данные +77779185334"
        cashback = order.course.current_price * (settings.CASH_PERCENT / 100)
        course_price = order.course.current_price

        if order.course.cash_type == 1:
            course_price -= cashback

        ione = course_price * (order.course.commission / 100)
        teacher = order.course.current_price - ione - cashback

        ioka = order.price * (settings.IOKA_PERCENT / 100)
        ione -= ioka

        order.course.proceeds_for_current_month += teacher
        order.course.save()

        if not order.customer_is_using_cashback:
            order.user.cashback_balance += cashback
        else:
            ione += cashback
            cashback_is_been_using = order.course.current_price - order.price
            order.user.cashback_balance -= cashback_is_been_using

        order.user.save()

        order.income_for_ione = ione
        order.save()

        order.is_paid = True
        order.save()

        if order.payment_type == "buy":
            MyCourse.objects.create(user=order.user, course=order.course, is_available_until=datetime.today() + relativedelta(months=order.course.access_months))
            order.course.course.number_of_students += 1
            order.course.course.save()
            return "<style>body { text-align: center; }</style>Покупка была успешна, теперь вам доступен курс, вы можете закрыть эту страницу и увидеть ваш курс в профиле"
        else:
            token = os.urandom(6)
            coupon = base64.b64encode(token).decode()
            Coupon.objects.create(user=order.user, course=order.course, coupon=coupon)
            return "<style>body { text-align: center; }</style>Покупка была успешна, теперь вам доступен купон этого курса, вы можете закрыть эту страницу и увидеть ваш купон в профиле"
    else:
        return "<style>body { text-align: center; }</style>Истекло время на оплату или же платеж уже был сделан. Подробнее об платеже можете увидеть <a href='" + order.checkout_url + "' target='_blank'>на этой странице</a>."


def success_course_renew_access_order_payment(order_id):
    order = get_object_or_404(CourseRenewAccessOrder, id=order_id)
    if not order.is_paid and not order.payment_time_is_expired():
        order.course.renew_access(order.months)
        order.is_paid = True
        order.save()

        ione = order.price * (60 / 100)
        teacher = order.price - ione

        ioka = order.price * (settings.IOKA_PERCENT / 100)
        ione -= ioka

        order.course.course.proceeds_for_current_month += teacher
        order.course.course.save()

        order.income_for_ione = ione
        order.save()

        return "<style>body { text-align: center; }</style>Покупка была успешна, теперь вам доступен курс, вы можете закрыть эту страницу и увидеть ваш курс в профиле"
    else:
        return "<style>body { text-align: center; }</style>Истекло время на оплату или же платеж уже был сделан. Подробнее об платеже можете увидеть <a href='" + order.checkout_url + "' target='_blank'>на этой странице</a>.  Перейти в <a href='/courses/user/profile/'>профиль</a>"
