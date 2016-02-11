from os import path
from pecan import request, redirect

def error(url, msg=None):
    """
    Helper for controller methods to do an internal redirect with
    either a url part like::

        error("/errors/not_allowed/")

    Or an http code::

        error(404)

    The ``msg`` argument is optional and would override the default error
    message for each error condition as defined in the ``ErrorController``
    methods.
    """
    code_to_url = {
        400: '/errors/invalid/',
        403: '/errors/forbidden/',
        404: '/errors/not_found/',
        405: '/errors/not_allowed/',
        500: '/errors/error/',
        503: '/errors/unavailable/',
    }

    if isinstance(url, int):
        url = code_to_url.get(url, 500)

    if msg:
        request.context['message'] = msg
    url = path.join(url, '?message=%s' % msg)
    redirect(url, internal=True)
