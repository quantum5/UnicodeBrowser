from UnicodeBrowser.unicode.models import CodePoint
import re

__author__ = 'xiaomao'


def search(keyword, start=None, limit=None):
    if start is None:
        start = 0
    piece = slice(start, (start + limit) if limit is not None else None)
    try:
        points = list(CodePoint.objects.filter(description__search=keyword)[piece].all())
    except NotImplementedError:
        words = keyword.split()
        blacklist = []
        query = CodePoint.objects
        for word in words:
            if word.startswith('-'):
                blacklist.append(re.compile(re.escape(word[1:]), re.I))
            elif word.startswith('+'):
                query = query.filter(description__icontains=word[1:])
            else:
                query = query.filter(description__icontains=word)

        def gen():
            for point in query.all():
                for black in blacklist:
                    if black.search(point.description):
                        break
                else:
                    yield point

        if blacklist:
            points = list(gen())[piece]
        else:
            points = list(query[piece].all())
    return points
