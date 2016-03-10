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
    @validate(schemas.mon_install_schema, handler="/errors/schema")
    def install_post(self):
        hosts = request.json.get('hosts')
        install_calamari = request.json.get('calamari', False)
        extra_vars = util.get_install_extra_vars(request.json)
        extra_vars['calamari'] = install_calamari
        identifier = str(uuid4())
        task = models.Task(
            identifier=identifier,
            endpoint=request.path,
        )
        # we need an explicit commit here because the command may finish before
        # we conclude this request
        models.commit()
        kwargs = dict(
            extra_vars=extra_vars,
            tags="package-install"
        )
        call_ansible.apply_async(
            args=([('mons', hosts)], identifier),
            kwargs=kwargs,
        )

        return task

    @expose(generic=True, template='json')
    def configure(self):
        error(405)

    @configure.when(method='POST', template='json')
    @validate(schemas.mon_configure_schema, handler="/errors/schema")
    def configure_post(self):
        hosts = util.parse_monitors([{
            "host": request.json['host'],
            "interface": request.json["monitor_interface"],
        }])
        monitors = request.json.get("monitors")
        # even with configuring we need to tell ceph-ansible
        # if we're working with upstream ceph or red hat ceph storage
        extra_vars = util.get_install_extra_vars(request.json)
        # this update will take everything in the ``request.json`` body and
        # just pass it in as extra-vars. That is the reason why optional values
        # like "calamari" are not looked up explicitly. If they are passed in
        # they will be used.
        extra_vars.update(request.json)
        if monitors:
            hosts.extend(util.parse_monitors(monitors))
            del extra_vars['monitors']
        del extra_vars['host']
        del extra_vars['monitor_interface']
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
            args=([('mons', hosts)], identifier),
            kwargs=kwargs,
        )

        return task
