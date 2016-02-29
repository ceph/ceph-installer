from os import path
import sys
import requests
import time
from textwrap import dedent
from tambo import Transport

from ceph_installer.cli import log, constants


class Task(object):

    help = "/api/tasks/ operations"
    options = []
    _help = dedent("""
    Human-readable task information: stdout, stderr, and the ability to "poll"
    a task that waits until the command completes to be able to show the output
    in a readable way.

    Usage::

        ceph-installer task $IDENTIFIER

    Options:

    --poll        Poll until the task has completed (either on failure or success)
    stdout        Retrieve the stdout output from the task
    stderr        Retrieve the stderr output from the task
    command       The actual command used to call ansible
    ended         The timestamp (in UTC) when the command completed
    started       The timestamp (in UTC) when the command started
    exit_code     The shell exit status for the process
    succeeded     Boolean value to indicate if process completed correctly
    """)

    def __init__(self, arguments):
        self.arguments = arguments
        self.tasks_url = path.join(constants.server_address, 'api/tasks')
        self.identifier = ''

    @property
    def request_url(self):
        url = path.join(self.tasks_url, self.identifier)
        # and add a trailing slash so that the request is done at the correct
        # canonical url
        if not url.endswith('/'):
            url = "%s/" % url
        return url

    def get(self, key):
        """
        :arg key: any actual key that can be present in the JSON output
        """
        log.info('requesting task at: %s' % self.request_url)
        response = requests.get(self.request_url)
        json = response.json()
        if response.status_code >= 400:
            return log.error(json['message'])
        try:
            value = json[key]
            log.info("%s: %s" % (key, value))
        except KeyError:
            return log.warning('no value found for: "%s"' % key)

    def summary(self):
        response = requests.get(self.request_url)
        json = response.json()
        if response.status_code >= 400:
            log.error(json['message'])
        for k, v in json.items():
            log.debug("%s: %s" % (k, v))

    def process_response(self, silent=False):
        response = requests.get(self.request_url)
        json = response.json()
        if response.status_code >= 400:
            if not silent:
                log.error(json['message'])
            return {}
        return json

    def poll(self):
        log.info('Polling task at: %s' % self.request_url)
        json = self.process_response()
        # JSON could be set to None
        completed = json.get('ended', False)
        while not completed:
            sequence = ['.', '..', '...', '....']
            for s in sequence:
                sys.stdout.write('\r' + ' '*80)
                string = "Waiting for completed task%s" % s
                sys.stdout.write('\r' + string)
                time.sleep(0.3)
                sys.stdout.flush()
            json = self.process_response(silent=True)
            completed = json.get('ended', False)
        sys.stdout.write('\r' + ' '*80)
        sys.stdout.flush()
        sys.stdout.write('\r'+'Task Completed!\n')
        for k, v in json.items():
            log.debug("%s: %s" % (k, v))

    def main(self):
        parser = Transport(self.arguments, options=self.options, check_help=True)
        parser.catch_help = self._help
        parser.parse_args()
        parser.catches_help()
        if not parser.unknown_commands:
            log.error("it is required to pass an identifer, but none was provided")
            raise SystemExit(1)
        self.identifier = parser.unknown_commands[-1]
        if parser.has('--poll'):
            return self.poll()

        for key in [
                'stdout', 'stderr', 'command', 'ended',
                'started', 'succeeded', 'exit_code']:
            if parser.has(key):
                return self.get(key)

        # if nothing else matches, just try to give a generic, full summary
        self.summary()
