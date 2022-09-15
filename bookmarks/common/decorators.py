from functools import wraps
from django.http import HttpResponseBadRequest


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def ajax_required(f):
    @wraps(f)
    def wrapper(request, *args, **kwargs):
        if not is_ajax(request):
            return HttpResponseBadRequest()
        return f(request, *args, **kwargs)
    return wrapper
