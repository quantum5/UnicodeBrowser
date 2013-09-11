from django.http import HttpResponse
from UnicodeBrowser.unicode.models import CodePoint

import json


def json_search(request, keyword):
    data = []
    try:
        points = list(CodePoint.objects.filter(description__search=keyword).all())
    except NotImplementedError:
        points = list(CodePoint.objects.filter(description__contains=keyword).all())
    for point in points:
        data.append(dict(id=point.id, desciption=point.description, block=point.block.fullname))
    return HttpResponse(json.dumps(data))
