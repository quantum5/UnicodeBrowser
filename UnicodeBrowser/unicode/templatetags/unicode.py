import os

from django import template
from django.contrib.staticfiles import finders
from django.utils.safestring import mark_safe
from django.conf import settings

__author__ = 'xiaomao'

register = template.Library()


@register.filter(name='to_entity')
def to_entity(value):
    return mark_safe('&#x{:04x};'.format(int(value)))


@register.simple_tag
def staticV(path):
    try:
        time = int(os.path.getmtime(finders.find(path)))
        return '%s%s?%s' % (settings.STATIC_URL, path, time)
    except OSError:
        return '%s%s' % (settings.STATIC_URL, path)
