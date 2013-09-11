from UnicodeBrowser.unicode.models import CodePoint
import re

__author__ = 'xiaomao'


def search(keyword):
    try:
        points = list(CodePoint.objects.filter(description__search=keyword).all())
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
            points = list(gen())
        else:
            points = list(query.all())
    return points
