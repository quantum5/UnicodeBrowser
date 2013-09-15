from django.core.cache import cache
from UnicodeBrowser.unicode.models import CodePoint
import re
from itertools import chain

__author__ = 'xiaomao'


def search(keyword, start=None, limit=None):
    if start is None:
        start = 0
    piece = slice(start, (start + limit) if limit is not None else None)
    keyword = [word[1:] if word.startswith('+') else word for word in keyword.split()]
    keyword.sort()
    key = 'search:' + '+'.join(keyword)
    keyword = ' '.join(keyword)
    cached = cache.get(key)
    if cached is not None:
        return cached[piece]

    words = keyword.split()
    query = CodePoint.objects
    for word in words:
        if word.startswith('-'):
            query = query.exclude(description__icontains=word[1:])
        else:
            query = query.filter(description__icontains=word)

    noncjk = query.all().exclude(block__name__contains='cjk')
    cjk = query.all().filter(block__name__contains='cjk').order_by('block__name')
    points = list(chain(noncjk, cjk))

    cache.set(key, points, None)
    return points[piece]
