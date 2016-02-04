import logging
from uuid import uuid4
from celery import shared_task
from mariner import util, models, process


logger = logging.getLogger(__name__)


@shared_task
def install(component, hosts, tags, request_path):
    """
    `component`: What component is it going to get installed: mon, rgw, osd, calamari
    """
    # TODO: figure out all the other component mappings
    component_map = {
        'mon': 'mons',
        'osd': 'osds',
    }
    identifier = str(uuid4())
    component_title = component_map[component]
    hosts_file = util.generate_inventory_file(component_title, hosts, identifier)
    command = process.make_ansible_command(hosts_file, identifier, tags=tags)
    models.Task(
        identifier=identifier,
        endpoint=request_path,
        command=' '.join(command),
    )
    # we need an explicit commit here because the command may finish before
    # we conclude this request
    models.commit()
    out, err, exit_code = process.run(command)
    task = models.Task.query.filter_by(identifier=identifier).first()
    task.succeeded = not exit_code
    task.stdout = out
    task.stderr = err
    models.commit()
