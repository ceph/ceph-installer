import logging
from celery import shared_task
from mariner import util, models, process


logger = logging.getLogger(__name__)


@shared_task
def install(component, hosts, tags, identifier):
    """
    `component`: What component is it going to get installed: mon, rgw, osd, calamari
    """
    # TODO: figure out all the other component mappings
    component_map = {
        'mon': 'mons',
        'osd': 'osds',
    }
    component_title = component_map[component]
    hosts_file = util.generate_inventory_file(component_title, hosts, identifier)
    command = process.make_ansible_command(hosts_file, identifier, tags=tags)
    task = models.Task.query.filter_by(identifier=identifier).first()
    task.command = ' '.join(command)
    # force a commit here so we can reference this command later if it fails
    models.commit()
    out, err, exit_code = process.run(command)
    task.succeeded = not exit_code
    task.stdout = out
    task.stderr = err
    models.commit()
