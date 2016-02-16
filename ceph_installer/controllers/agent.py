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

    @expose('json')
    def index(self):
        return dict()

    @expose(generic=True, template='json')
    def install(self):
        error(405)

    @install.when(method='POST', template='json')
    @validate(schemas.install_schema, handler="/errors/schema")
    def install_post(self):
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
        kwargs = dict(extra_vars=extra_vars, tags="package-install")
        call_ansible.apply_async(
            args=('agent', hosts, identifier),
            kwargs=kwargs,
        )

        return task

    @expose(generic=True, template='json')
    def configure(self):
        error(405)

    # we need validation here
    @configure.when(method='POST', template='json')
    def configure_post(self):
        hosts = [request.json.get('host')]
        # even with configuring we need to tell ceph-ansible
        # if we're working with upstream ceph or red hat ceph storage
        extra_vars = util.get_install_extra_vars(request.json)
        identifier = str(uuid4())
        task = models.Task(
            identifier=identifier,
            endpoint=request.path,
        )
        # we need an explicit commit here because the command may finish before
        # we conclude this request
        models.commit()
        kwargs = dict(extra_vars=extra_vars, skip_tags="package-install")
        call_ansible.apply_async(
            args=('agent', hosts, identifier),
            kwargs=kwargs,
        )

        return task
