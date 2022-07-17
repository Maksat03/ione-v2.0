from django.urls import reverse

from .forms import PasswordChangeForm, ChangeEmailForm, NewPasswordForm
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from my_courses.models import MyCourse

from . import services as auth_services
from courses import services as courses_services
from .forms import ChangeUserDataForm


def profile_page_view(request):
	if request.user.is_authenticated:
		if hasattr(request.user, "teacher"):
			return redirect(reverse("teacher_page"))
		return render(
			request=request,
			template_name="profilePage.html",
			context={
				"favourite_courses": request.user.favourite_courses.all(),
				"my_courses": MyCourse.objects.filter(user_id=request.user.id),
				"coupons": courses_services.get_user_coupons_in_n_x_3_matrix(request.user),
				"courses_with_certificate": courses_services.get_user_courses_with_certificate_in_n_x_3_matrix(request.user),
				"change_user_data_form": ChangeUserDataForm(instance=request.user),
				"change_password_form": PasswordChangeForm(request.user),
				"change_email_form": ChangeEmailForm()
			}
		)
	return redirect("/courses/#log-zatemnenie")


def sign_up_view(request):
	if request.method == "POST":
		response = auth_services.create_new_user_and_send_confirmation_link(request)
		return JsonResponse(response)
	return redirect("/")


def login_view(request):
	if request.is_ajax() and request.method == "POST":
		response = auth_services.logout_from_other_devices_and_login_only_this_user(request)
		return JsonResponse(response)
	return redirect("/")


def change_user_data_view(request):
	if request.is_ajax() and request.method == "POST" and request.user.is_authenticated:
		response = auth_services.change_user_data(request.user, request.POST, request.FILES)
		return JsonResponse(response)
	return JsonResponse({"success": False, "errors": {"first_name": [
		{"message": "You were logged in by another device so this device was unauthorized"}]}})


def activate(request, uidb64, token):
	response = auth_services.acc_activate(request, uidb64, token)
	return response


def change_password_view(request):
	if request.is_ajax() and request.method == "POST" and request.user.is_authenticated:
		response = auth_services.change_password(request)
		return JsonResponse(response)
	return JsonResponse({"success": False, "errors": {"old_password": ["You were logged in by another device so this device was unauthorized"]}})


def change_email_view(request):
	if request.is_ajax() and request.method == "POST" and request.user.is_authenticated:
		response = auth_services.change_email(request.user, request.POST)
		return JsonResponse(response)
	return JsonResponse({"success": False, "errors": {"password": ["You were logged in by another device so this device was unauthorized"]}})


def activate_changing_email_view(request, email, uidb64, token):
	response = auth_services.activate_changing_email(request, email, uidb64, token)
	return response


def reset_password_view(request):
	if request.method == "POST" and request.is_ajax():
		response = auth_services.reset_password(request.body)
		return JsonResponse(response)
	return redirect("/")


def reset_password_to_view(request, uidb64, token):
	if request.method == "GET":
		return render(request, "gmail_pass.html", {"new_password_form": NewPasswordForm(request.user)})
	else:
		form = NewPasswordForm(request.user, request.POST)
		if form.is_valid():
			user, is_correct_token = auth_services.reset_password_activation(uidb64, token)

			if is_correct_token:
				user.set_password(form.cleaned_data["new_password1"])
				user.save()
				return render(request, "gmail_conf.html")
			return HttpResponse("Invalid token")
		return render(request, "gmail_pass.html", {"new_password_form": form, "info": form.errors})
