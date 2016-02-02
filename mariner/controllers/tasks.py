from pecan import expose


class TasksController(object):

    @expose
    def install(self):
        return {}

    @expose
    def configure(self):
        return {}
