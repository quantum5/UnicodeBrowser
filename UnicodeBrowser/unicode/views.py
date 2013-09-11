from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render_to_response
import UnicodeBrowser.unicode.search

import json


def json_search(request, keyword):
    data = []
    for point in UnicodeBrowser.unicode.search.search(keyword):
        data.append(dict(id=point.id, desciption=point.description, block=point.block.fullname))
    return HttpResponse(json.dumps(data))


def search(request):
    context = {}
    if 'q' in request.GET:
        paginator = Paginator(UnicodeBrowser.unicode.search.search(request.GET['q']), 50)
        page = request.GET.get('page')
        try:
            context['codepoints'] = paginator.page(page)
        except PageNotAnInteger:
            context['codepoints'] = paginator.page(1)
        except EmptyPage:
            context['codepoints'] = paginator.page(paginator.num_pages)
        context['query'] = request.GET['q']
    return render_to_response('search.xhtml', context)
