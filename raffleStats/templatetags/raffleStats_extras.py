from django import template

register = template.Library()

@register.filter
def index(indexable, i):
    return indexable[i]

@register.filter
def value_range(value):
    return range(value)
