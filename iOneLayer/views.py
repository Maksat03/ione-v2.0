from django.shortcuts import render

from project.settings import iOneLayerKey
from django.http import JsonResponse
from . import services


def where_to_connect_view(request):
    key = request.GET.get("key")
    if key == iOneLayerKey:
        server = services.get_ionelayer_server_with_minimum_connection_count()
        return JsonResponse({"server-ip-addr": server.ip_addr, "server-port": server.port})
    return JsonResponse({"err_info": "Invalid KEY"})


def add_ip_to_db_view(request):
    key = request.GET.get("key")
    if key == iOneLayerKey:
        services.add_ip_to_db(request)
        return JsonResponse({"success": True})
    return JsonResponse({"err_info": "Invalid KEY"})


def remove_ip_from_db_view(request):
    key = request.GET.get("key")
    if key == iOneLayerKey:
        services.remove_ip_from_db(request)
        return JsonResponse({"success": True})
    return JsonResponse({"err_info": "Invalid KEY"})


def ionelayer_is_active_view(request):
    return render(request, "iOneLayerIsActive.html")
