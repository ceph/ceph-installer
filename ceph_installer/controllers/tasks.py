from pecan import expose

from ceph_installer.models import Task
from ceph_installer.controllers import error


class TaskController(object):

    def __init__(self, task_id):
        self.task = Task.query.filter_by(identifier=task_id).first()
        if not self.task:
            error(404, '%s is not available' % task_id)

    @expose('json')
    def index(self):
        return self.task


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
