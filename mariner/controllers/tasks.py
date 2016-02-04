from pecan import expose
from datetime import datetime

from mariner.models import Task
from mariner.controllers import error


class TaskController(object):

    def __init__(self, task_id):
        self.task = Task.query.filter_by(identifier=task_id).first()
        if not self.task:
            error('/errors/not_found/', '%s task was not found' % task_id)

    @expose(generic=True, template='json')
    def completed(self):
        error('/errors/not_allowed/')

    @completed.when(method='POST', template='json')
    def completed_post(self):
        self.task.ended = datetime.utcnow()
        with open(self.task.stdout_file, 'r') as stdout_file:
            self.task.stdout = stdout_file.read()

        with open(self.task.stderr_file, 'r') as stderr_file:
            self.task.stderr = stderr_file.read()

        return {}

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
