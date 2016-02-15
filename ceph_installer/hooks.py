from celery.task.control import inspect
from errno import errorcode
from ceph_installer import models
from ceph_installer.util import which
from pecan import render
from pecan.hooks import PecanHook
from sqlalchemy.exc import OperationalError
from webob.exc import WSGIHTTPException
import logging


logger = logging.getLogger(__name__)


class SystemCheckError(Exception):

    def __init__(self, message):
        self.message = message


def ansible_exists():
    """
    Perform a simple check to see if ``ansibl-playbook`` executable is present
    in the system where the service is running.
    """
    ansible_path = which('ansible-playbook')
    if not ansible_path:
        raise SystemCheckError('Could not find ansible in system paths')


def celery_has_workers():
    """
    The ``stats()`` call will return different stats/metadata information about
    celery worker(s).  An empty/None result will mean that there aren't any
    celery workers in use.
    """
    stats = inspect().stats()
    if not stats:
        raise SystemCheckError('No running Celery worker was found')


def rabbitmq_is_running():
    """
    If checking for worker stats, an ``IOError`` may be raised depending on the
    problem for the RabbitMQ connection.
    """
    try:
        celery_has_workers()
    except IOError as e:
        msg = "Error connecting to RabbitMQ: " + str(e)
        if len(e.args):
            if errorcode.get(e.args[0]) == 'ECONNREFUSED':
                msg = "RabbitMQ is not running or not reachable"
        raise SystemCheckError(msg)


def database_connection():
    """
    A very simple connection that should succeed if there is a good/correct
    database connection.
    """
    try:
        models.Task.get(1)
    except OperationalError as exc:
        raise SystemCheckError(
            "Could not connect or retrieve information from the database: %s" % exc.message)


class SystemCheckHook(PecanHook):
    """
    Perform a series of system checks which prevents the service from doing any
    work unless everything required checks out.
    """

    def before(self, state):
        """
        Executed before a controller gets called. When an error condition is
        detected (one of the callables raises a ``SystemCheckError``) it sets
        the response status to 500 and returns a JSON response with the
        appropriate reason.
        """
        for check in [ansible_exists, rabbitmq_is_running, celery_has_workers,
                      database_connection]:
            try:
                check()
            except SystemCheckError as system_error:
                message = render('json', {'message': system_error.message})
                raise WSGIHTTPException(content_type='application/json', body=message)
