from pecan import expose, abort
from mariner.controllers import error


class MONController(object):

    @expose('json')
    def index(self):
        # TODO: allow some autodiscovery here so that clients can see what is
        # available
        return dict()

    @expose(generic=True, template='json')
    def install(self):
        error('/errors/not_allowed/')

    # we need validation here
    @install.when(method='POST', template='json')
    def install_post(self):
        return {}

    @expose(generic=True, template='json')
    def configure(self):
        error('/errors/not_allowed/')

    # we need validation here
    @configure.when(method='POST', template='json')
    def configure_post(self):
        return {}
