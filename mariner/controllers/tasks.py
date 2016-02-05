import os
from pecan import expose
from datetime import datetime

from mariner.models import Task
from mariner.controllers import error


class TaskController(object):

    def __init__(self, task_id):
        self.task = Task.query.filter_by(identifier=task_id).first()
        if not self.task:
            error(404, '%s is not avilable' % task_id)

    def read_log(self, path):
        if not path:
            return ''
        if not os.path.exists(path) or not os.path.isfile(path):
            return ''
        with open(path, 'r') as log_file:
            return log_file.read()


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
