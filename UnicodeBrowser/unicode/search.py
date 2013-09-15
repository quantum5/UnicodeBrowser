from django.core.cache import cache
from UnicodeBrowser.unicode.models import CodePoint
from django.conf import settings

from itertools import chain
from functools import partial

__author__ = 'xiaomao'

better_sort = getattr(settings, 'BETTER_SORT', True)


def get_bigrams(string):
    """
    Takes a string and returns a list of bigrams
    """
    s = string.lower()
    return {s[i:i+2] for i in xrange(len(s) - 1)}


def string_similarity(str1, str2):
    """
    Perform bigram comparison between two strings
    and return a percentage match in decimal form
    """
    pairs1 = get_bigrams(str1)
    pairs2 = get_bigrams(str2)
    intersection = pairs1 & pairs2
    return (2.0 * len(intersection)) / (len(pairs1) + len(pairs2))


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
    if better_sort:
        sorter = lambda point: round(string_similarity(keyword, point.description), 1)
        points = list(noncjk)
        points.sort(key=sorter, reverse=True)
        cjk = list(cjk)
        cjk.sort(key=sorter, reverse=True)
        points.extend(cjk)
    else:
        points = list(chain(noncjk, cjk))

    cache.set(key, points, None)
    return points[piece]
