import logging

from datetime import datetime
from celery import shared_task
from mariner import util, models, process


logger = logging.getLogger(__name__)


@shared_task
def install(component, hosts, identifier, tags="install-packages"):
    """
    ``component``: What component is it going to get installed: mon, rgw, osd, calamari
    ``hosts``: A list of hosts to install, these host must be resolvable
    ``tags``: The tags as a comma-delimeted string that represents all the tags
              this ansible call should follow. For example "install-packages,other-tag"
    ``identifier``: The UUID identifer for the task object so this function can capture process
                    metadata and persist it to the database
    """
    component_title = "%s%s" % (component, '' if component.endswith('s') else 's')
    hosts_file = util.generate_inventory_file(component_title, hosts, identifier)
    command = process.make_ansible_command(hosts_file, identifier, tags=tags)
    task = models.Task.query.filter_by(identifier=identifier).first()
    task.command = ' '.join(command)
    task.started = datetime.now()
    # force a commit here so we can reference this command later if it fails
    models.commit()
    out, err, exit_code = process.run(command)
    task.succeeded = not exit_code
    task.exit_code = exit_code
    task.stdout = out
    task.stderr = err
    task.ended = datetime.now()
    models.commit()
