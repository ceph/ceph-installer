from pecan import expose, response, request


class ErrorController(object):

    @expose('json')
    def schema(self, **kw):
        response.status = 400
        return dict(message=str(request.validation_error))

    @expose('json')
    def invalid(self, **kw):
        msg = kw.get(
            'message',
            'invalid request'
        )
        response.status = 400
        return dict(message=msg)

    @expose('json')
    def forbidden(self, **kw):
        msg = kw.get(
            'message',
            'forbidden'
        )
        response.status = 403
        return dict(message=msg)

    @expose('json')
    def not_found(self, **kw):
        msg = kw.get(
            'message',
            'resource was not found'
        )
        response.status = 404
        return dict(message=msg)

    @expose('json')
    def not_allowed(self, **kw):
        msg = kw.get(
            'message',
            'method %s not allowed for "%s"' % (request.method, request.path)
        )
        response.status = 405
        return dict(message=msg)

    @expose('json')
    def unavailable(self, **kw):
        msg = kw.get(
            'message',
            'service unavailable',
        )
        response.status = 503
        return dict(message=msg)

    @expose('json')
    def error(self, **kw):
        msg = kw.get(
            'message',
            'an error has occured',
        )
        response.status = 500
        return dict(message=msg)
