import logging

from pecan import expose, request
from pecan.ext.notario import validate
from uuid import uuid4

from ceph_installer.controllers import error
from ceph_installer.tasks import call_ansible
from ceph_installer import schemas
from ceph_installer import models
from ceph_installer import util


logger = logging.getLogger(__name__)


class AgentController(object):

    @expose(generic=True, template='json')
    def index(self):
        error(405)

    @index.when(method='POST', template='json')
    @validate(schemas.install_schema, handler="/errors/schema")
    def install(self):
        hosts = request.json.get('hosts')
        extra_vars = util.get_install_extra_vars(request.json)
        identifier = str(uuid4())
        task = models.Task(
            identifier=identifier,
            endpoint=request.path,
        )
        # we need an explicit commit here because the command may finish before
        # we conclude this request
        models.commit()
        kwargs = dict(extra_vars=extra_vars)
        call_ansible.apply_async(
            args=('agent', hosts, identifier),
            kwargs=kwargs,
        )

        return task
