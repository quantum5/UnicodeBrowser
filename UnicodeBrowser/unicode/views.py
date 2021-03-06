from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_page
from UnicodeBrowser.unicode.models import Font
import UnicodeBrowser.unicode.search

import json


def json_search(request, keyword):
    data = []
    for point in UnicodeBrowser.unicode.search.search(keyword):
        data.append(dict(id=point.id, desciption=point.description, block=point.block.fullname))
    return HttpResponse(json.dumps(data))


def search(request):
    context = {}
    if 'q' in request.GET and request.GET['q']:
        paginator = Paginator(UnicodeBrowser.unicode.search.search(request.GET['q']), 200)
        page = request.GET.get('page')
        try:
            context['codepoints'] = paginator.page(page)
        except PageNotAnInteger:
            context['codepoints'] = paginator.page(1)
        except EmptyPage:
            context['codepoints'] = paginator.page(paginator.num_pages)
        context['query'] = request.GET['q']
        context['fonts'] = fonts = set()
        for point in context['codepoints']:
            if point.block.font is not None:
                fonts.add(point.block.font)
    return render_to_response('search.xhtml', context)

@cache_page(None)
def fonts(request):
    return render_to_response('fonts.css', dict(fonts=Font.objects.all()), mimetype='text/css')

