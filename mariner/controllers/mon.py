from pecan import expose, request
import logging
from mariner.controllers import error
from mariner.tasks import install


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
        hosts = request.json.get('hosts')
        tags = 'package-install'
        install.apply_async(
            ('mon', hosts, tags, request.path),
        )

        return {}

    @expose(generic=True, template='json')
    def configure(self):
        error('/errors/not_allowed/')

    # we need validation here
    @configure.when(method='POST', template='json')
    def configure_post(self):
        return {}
