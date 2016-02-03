from os import path
from pecan import request, redirect


def error(url, msg=None):
    if msg:
        request.context['message'] = msg
    url = path.join(url, '?message=%s' % msg)
    redirect(url, internal=True)
