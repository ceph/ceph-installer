import logging
from pecan import expose, response, request


logger = logging.getLogger(__name__)
schema_logger = logging.getLogger("%s.schema" % __name__)


class ErrorController(object):

    @expose('json')
    def schema(self, **kw):
        response.status = 400
        schema_logger.error(request.validation_error)
        try:
            path = request.validation_error._format_path()
            message = '%s%sfailed validation, %s' % (
                path,
                '' if path.endswith(' ') else ' ',
                request.validation_error.reason
            )
        except AttributeError:
            message = "invalid JSON was received"
        return dict(message=message)

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
