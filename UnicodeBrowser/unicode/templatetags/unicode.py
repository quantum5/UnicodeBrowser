from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

__author__ = 'xiaomao'


register = template.Library()

@register.filter(name='to_entity')
def to_entity(value):
    return mark_safe('&#x{:04x};'.format(int(value)))


@register.filter(name='to_br')
@stringfilter
def to_br(value):
    return mark_safe(value.replace('\n', '<br/>'))