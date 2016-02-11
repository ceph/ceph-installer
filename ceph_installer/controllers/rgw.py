import logging

from pecan import expose, request
from pecan.ext.notario import validate
from uuid import uuid4

from ceph_installer.controllers import error
from ceph_installer.tasks import install
from ceph_installer import schemas
from ceph_installer import models

logger = logging.getLogger(__name__)


class RGWController(object):

    @expose('json')
    def index(self):
        # TODO: allow some autodiscovery here so that clients can see what is
        # available
        return dict()

    @expose(generic=True, template='json')
    def install(self):
        error(405)

    @install.when(method='POST', template='json')
    @validate(schemas.install_schema, handler="/errors/schema")
    def install_post(self):
        hosts = request.json.get('hosts')
        identifier = str(uuid4())
        task = models.Task(
            identifier=identifier,
            endpoint=request.path,
        )
        # we need an explicit commit here because the command may finish before
        # we conclude this request
        models.commit()
        install.apply_async(
            ('rgw', hosts, identifier),
        )

        return task

    @expose('json')
    def configure(self):
        return {}
