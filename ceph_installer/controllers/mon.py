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
        verbose_ansible = request.json.get('verbose', False)
        extra_vars = util.get_install_extra_vars(request.json)
        extra_vars['calamari'] = install_calamari
        identifier = str(uuid4())
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
        monitor_mapping = dict(host=request.json['host'])

        # Only add interface and address if they exist
        for key in ['interface', 'address']:
            try:
                monitor_mapping[key] = request.json[key]
            except KeyError:
                pass
        hosts = util.parse_monitors([monitor_mapping])
        verbose_ansible = request.json.get('verbose', False)
        monitors = request.json.get("monitors", [])
        monitors = util.validate_monitors(monitors, request.json["host"])
        # even with configuring we need to tell ceph-ansible
        # if we're working with upstream ceph or red hat ceph storage
        extra_vars = util.get_install_extra_vars(request.json)
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
        if monitors:
            hosts.extend(util.parse_monitors(monitors))
            del extra_vars['monitors']
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
            args=([('mons', hosts)], identifier),
            kwargs=kwargs,
        )

        return task
