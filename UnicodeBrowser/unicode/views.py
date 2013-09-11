from django.http import HttpResponse
from UnicodeBrowser.unicode.search import search

import json


def json_search(request, keyword):
    data = []
    for point in search(keyword):
        data.append(dict(id=point.id, desciption=point.description, block=point.block.fullname))
    return HttpResponse(json.dumps(data))
