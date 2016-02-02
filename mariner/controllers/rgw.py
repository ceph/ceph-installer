from pecan import expose


class RGWController(object):


    @expose
    def install(self):
        return {}

    @expose
    def configure(self):
        return {}
