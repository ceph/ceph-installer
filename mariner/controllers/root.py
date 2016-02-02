from pecan import expose
from mariner.controllers import tasks, mon, osd, rgw, calamari


class ApiController(object):

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
