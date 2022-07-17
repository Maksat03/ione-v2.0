from django.db import models


class Server(models.Model):
    ip_addr = models.CharField(max_length=20)
    port = models.IntegerField()
    is_active = models.BooleanField(default=True)


class Connection(models.Model):
    server = models.ForeignKey(Server, on_delete=models.PROTECT)
    user_ip_addr = models.CharField(max_length=20)
