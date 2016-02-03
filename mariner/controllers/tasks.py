from pecan import expose

from mariner.models import Task
from mariner.controllers import error


class TaskController(object):

    def __init__(self, task_id):
        self.task = Task.query.filter_by(identifier=task_id).first()
        if not self.task:
            error('/errors/not_found/', '%s task was not found' % task_id)


class TasksController(object):

    @expose('json')
    def index(self):
        return Task.query.all()

    @expose('json')
    def install(self):
        return {}

    @expose('json')
    def configure(self):
        return {}

    @expose()
    def _lookup(self, task_id, *remainder):
        return TaskController(task_id), remainder
