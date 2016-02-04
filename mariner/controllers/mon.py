import os
from pecan import expose, request
import logging
from uuid import uuid4
from mariner.controllers import error
from mariner import process, models, util


logger = logging.getLogger(__name__)


class MONController(object):

    @expose('json')
    def index(self):
        # TODO: allow some autodiscovery here so that clients can see what is
        # available
        return dict()

    @expose(generic=True, template='json')
    def install(self):
        error('/errors/not_allowed/')

    # we need validation here
    @install.when(method='POST', template='json')
    def install_post(self):
        identifier = str(uuid4())
        # VALIDATIONNNNNN!!!! We can't do this without hosts
        hosts = request.json.get('hosts')
        hosts_file = util.generate_inventory_file('mons', hosts, identifier)
        tags = 'package-install'
        stdout = process.temp_file(identifier, 'stdout')
        stderr = process.temp_file(identifier, 'stderr')
        command = process.make_ansible_command(stderr, stdout, hosts_file, identifier, tags=tags)
        task = models.Task(
            identifier=identifier,
            endpoint=request.path,
            command=command
        )
        logger.debug('running command: %s', command)
        os.system(command)
        return {}

    @expose(generic=True, template='json')
    def configure(self):
        error('/errors/not_allowed/')

    # we need validation here
    @configure.when(method='POST', template='json')
    def configure_post(self):
        return {}
