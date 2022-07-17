from django.db import models
from django.shortcuts import reverse


class Category(models.Model):
    title = models.CharField(max_length=50)
    parent_category = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title


class Section(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey('Category', on_delete=models.PROTECT, null=True, blank=True)
    background_image = models.ImageField(upload_to="section-background-images/%Y/%m/%d/", default='section-background-images/default.png')
    background_image_mobile = models.ImageField(upload_to="section-background-images/%Y/%m/%d/", default='section-background-images/default_mobile.png')
    similar_sections = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("section", kwargs={"section_pk": self.pk})

    def get_courses(self):
        return self.courses.filter(is_last_edition=True)
