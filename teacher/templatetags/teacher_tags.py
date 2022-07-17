from django import template
from teacher.forms import PublishCourseRequestForm


register = template.Library()


@register.simple_tag(name="get_publish_course_request_form")
def get_publish_course_request_form():
    return PublishCourseRequestForm()
