from django import template
from iOneCourses.models import iOneNews


register = template.Library()


@register.simple_tag(name="get_ione_news_list")
def get_ione_news_list():
    return iOneNews.objects.all()
