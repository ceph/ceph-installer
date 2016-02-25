from pecan import response, expose
from ceph_installer.hooks import system_checks, SystemCheckError


class StatusController(object):

    @expose('json')
    def index(self):
        for check in system_checks:
            try:
                check()
            except SystemCheckError as system_error:
                response.status = 500
                return {'message': system_error.message}
        return dict(message="ok")
