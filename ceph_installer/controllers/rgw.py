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
        extra_vars = util.get_install_extra_vars(request.json)
        verbose_ansible = request.json.get('verbose', False)
        task = models.Task(
            request=request,
            identifier=identifier,
            endpoint=request.path,
        )
        # we need an explicit commit here because the command may finish before
        # we conclude this request
        models.commit()
        kwargs = dict(
            extra_vars=extra_vars,
            tags="package-install",
            verbose=verbose_ansible,
        )
        call_ansible.apply_async(
            args=([('rgws', hosts)], identifier),
            kwargs=kwargs,
        )

        return task

    @expose(generic=True, template='json')
    def configure(self):
        error(405)

    @configure.when(method='POST', template='json')
    @validate(schemas.rgw_configure_schema, handler="/errors/schema")
    def configure_post(self):
        hosts = [request.json['host']]
        # even with configuring we need to tell ceph-ansible
        # if we're working with upstream ceph or red hat ceph storage
        verbose_ansible = request.json.get('verbose', False)
        extra_vars = util.get_install_extra_vars(request.json)
        monitor_hosts = util.parse_monitors(request.json["monitors"])
        # this update will take everything in the ``request.json`` body and
        # just pass it in as extra-vars. That is the reason why optional values
        # like "calamari" are not looked up explicitly. If they are passed in
        # they will be used.
        extra_vars.update(request.json)
        if 'verbose' in extra_vars:
            del extra_vars['verbose']
        if 'conf' in extra_vars:
            extra_vars['ceph_conf_overrides'] = request.json['conf']
            del extra_vars['conf']
        if "cluster_name" in extra_vars:
            extra_vars["cluster"] = extra_vars["cluster_name"]
            del extra_vars["cluster_name"]
        del extra_vars['host']
        extra_vars.pop('interface', None)
        extra_vars.pop('address', None)
        identifier = str(uuid4())
        task = models.Task(
            request=request,
            identifier=identifier,
            playbook="infrastructure-playbooks/rgw-standalone.yml",
            endpoint=request.path,
        )
        # we need an explicit commit here because the command may finish before
        # we conclude this request
        models.commit()
        kwargs = dict(
            extra_vars=extra_vars,
            skip_tags="package-install",
            verbose=verbose_ansible,
        )
        call_ansible.apply_async(
            args=([('rgws', hosts), ('mons', monitor_hosts)], identifier),
            kwargs=kwargs,
        )

        return task
