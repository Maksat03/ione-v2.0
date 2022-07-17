from django.db import models


class iOneNews(models.Model):
    created_at = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=255)
    text = models.TextField()
