import logging

from pecan import expose, request
from pecan.ext.notario import validate
from uuid import uuid4

from mariner.controllers import error
from mariner.tasks import install
from mariner import schemas
from mariner import models


logger = logging.getLogger(__name__)


class MONController(object):

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
            ('mon', hosts, identifier),
        )

        return task

    @expose(generic=True, template='json')
    def configure(self):
        error(405)

    # we need validation here
    @configure.when(method='POST', template='json')
    def configure_post(self):
        return {}
