from pecan import expose


class RGWController(object):

    @expose('json')
    def index(self):
        # TODO: allow some autodiscovery here so that clients can see what is
        # available
        return dict()

    @expose('json')
    def install(self):
        return {}

    @expose('json')
    def configure(self):
        return {}
