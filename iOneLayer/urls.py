from django.urls import path
from .views import where_to_connect_view, add_ip_to_db_view, remove_ip_from_db_view, ionelayer_is_active_view


urlpatterns = [
    path("", ionelayer_is_active_view),
    path("where_to_connect/", where_to_connect_view),
    path("add_ip_to_db/", add_ip_to_db_view),
    path("remove_ip_from_db/", remove_ip_from_db_view)
]
