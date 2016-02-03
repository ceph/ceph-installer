from pecan import expose
from mariner.controllers import tasks, mon, osd, rgw, calamari, errors


class ApiController(object):

    @expose('json')
    def index(self):
        # TODO: allow some autodiscovery here so that clients can see what is
        # available
        return dict()

    tasks = tasks.TasksController()
    mon = mon.MONController()
    osd = osd.OSDController()
    rgw = rgw.RGWController()
    calamari = calamari.CalamariController()


class RootController(object):

    @expose('json')
    def index(self):
        return dict()

    api = ApiController()
    errors = errors.ErrorController()
