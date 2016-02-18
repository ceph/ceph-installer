import os
import logging

from datetime import datetime
from celery import shared_task
from ceph_installer import util, models, process


logger = logging.getLogger(__name__)


@shared_task
def call_ansible(inventory, identifier, tags="", skip_tags="", extra_vars=None):
    """
    This task builds an ansible-playbook command and runs it.

    ``inventory``: A list of tuples that details an ansible inventory. For example:
                   [('mons', ['mon1.host', 'mon2.host']), ('osds', ['osd1.host'])]
    ``tags``: The tags as a comma-delimeted string that represents all the tags
              this ansible call should follow. For example "package-install, other-tag"
    ``skip_tags``: The tags as a comma-delimeted string that represents all the tags
                   this ansible call should skip. For example "package-install, other-tag"
    ``identifier``: The UUID identifer for the task object so this function can capture process
                    metadata and persist it to the database
    """
    if not extra_vars:
        extra_vars = dict()
    hosts_file = util.generate_inventory_file(inventory, identifier)
    command = process.make_ansible_command(hosts_file, identifier, tags=tags, extra_vars=extra_vars, skip_tags=skip_tags)
    task = models.Task.query.filter_by(identifier=identifier).first()
    task.command = ' '.join(command)
    task.started = datetime.now()
    # force a commit here so we can reference this command later if it fails
    models.commit()
    working_dir = util.get_playbook_path()
    working_dir = os.path.split(working_dir)[0]
    # ansible depends on relative pathing to figure out how to load
    # plugins, among other things. Setting the current working directory
    # for this subprocess call to the directory where the playbook resides
    # allows ansible to properly find action plugins defined in ceph-ansible.
    kwargs = dict(cwd=working_dir)
    out, err, exit_code = process.run(command, **kwargs)
    task.succeeded = not exit_code
    task.exit_code = exit_code
    task.stdout = out
    task.stderr = err
    task.ended = datetime.now()
    models.commit()
