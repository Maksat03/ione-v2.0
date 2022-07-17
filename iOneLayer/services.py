from iOneLayer.models import Server, Connection


def user_is_using_ionelayer(request):
    user_ip_addr = _get_client_ip(request)
    if Connection.objects.filter(user_ip_addr=user_ip_addr).count() > 0:
        return True
    return False


def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_ionelayer_server_with_minimum_connection_count():
    servers = list(Server.objects.filter(is_active=True))
    connections = list()

    for server in servers:
        connections.append(Connection.objects.filter(server=server).count())

    index_of_min_count_of_connections = connections.index(min(connections))
    return servers[index_of_min_count_of_connections]


def add_ip_to_db(request):
    ip = request.GET.get("ip")
    server_ip = _get_client_ip(request)
    server = Server.objects.get(ip_addr=server_ip)
    Connection.objects.create(server=server, user_ip_addr=ip)


def remove_ip_from_db(request):
    ip = request.GET.get("ip")
    server_ip = _get_client_ip(request)
    server = Server.objects.get(ip_addr=server_ip)
    connections = Connection.objects.filter(server=server, user_ip_addr=ip)
    for connection in connections:
        connection.delete()