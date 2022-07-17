import jwt

from . import services
from project import settings
from django.http import HttpResponse


def ioka_payment_success_view(request, order_obj_id):
    try:
        order_id = jwt.decode(order_obj_id, settings.ORDER_OBJ_ID_JWT_KEY, algorithms=["HS256"])["order_obj_id"]
    except jwt.exceptions.InvalidSignatureError:
        return HttpResponse("Signature verification failed")

    if order := request.GET.get("order", None):
        if order == "course_order":
            return HttpResponse(services.success_course_order_payment(order_id))
        elif order == "course_renew_access_order":
            return HttpResponse(services.success_course_renew_access_order_payment(order_id))

    return HttpResponse("No order")
