from django import template

register = template.Library()


@register.filter(name='rating')
def rating(value):
    return value * '★'
