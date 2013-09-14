from UnicodeBrowser.unicode.models import CodePoint
import re
from itertools import chain

__author__ = 'xiaomao'


def search(keyword, start=None, limit=None):
    if start is None:
        start = 0
    piece = slice(start, (start + limit) if limit is not None else None)
    try:
        query = CodePoint.objects.filter(description__search=keyword)[piece].all()
        noncjk = query.all().exclude(block__name__contains='cjk')
        cjk = query.all().filter(block__name__contains='cjk').order_by('block__name')
        points = list(chain(noncjk, cjk))[piece]
    except NotImplementedError:
        words = keyword.split()
        blacklist = []
        query = CodePoint.objects
        for word in words:
            if word.startswith('-'):
                query = query.exclude(description__icontains=word[1:])
            elif word.startswith('+'):
                query = query.filter(description__icontains=word[1:])
            else:
                query = query.filter(description__icontains=word)

        noncjk = query.all().exclude(block__name__contains='cjk')
        cjk = query.all().filter(block__name__contains='cjk').order_by('block__name')
        points = list(chain(noncjk, cjk))[piece]
    return points
