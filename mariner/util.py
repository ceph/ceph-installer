import os
import pecan
import tempfile
import logging

logger = logging.getLogger(__name__)


def generate_inventory_file(group_name, hosts, task_uuid, tmp_dir=None):
    """
    Generates a host file to use with an ansible-playbook call.

    Given a group_name, a lists of hosts and a task UUID a file
    will be written to disk and a path to the file will be returned.
    """
    result = []
    result.append("[{0}]".format(group_name))
    if not isinstance(hosts, list):
        hosts = [hosts]
    result.extend(hosts)
    result_str = "\n".join(result)
    # if not None the NamedTemporaryFile will be created in the given directory
    tempfile.tempdir = tmp_dir
    inventory_file = tempfile.NamedTemporaryFile(prefix="{0}_".format(task_uuid), delete=False)
    inventory_file.write(result_str)
    inventory_file.close()
    return inventory_file.name


def api_endpoint(endpoint=None, *args):
    """
    Puts together the API url for mariner, so that we can talk to it. Optionally, the endpoint
    argument allows to return the correct url for specific needs. For example, to create a new task
    with a distinct identifier::

        >>> api_endpoint('tasks', str(uuid()))
        >>> "http://0.0.0.0/api/tasks/47e9a7bc-e27a-4cb3-ab7d-34c54381323f/"

    """
    server = pecan.conf['server']['host']
    port = pecan.conf['server']['port']
    base = "http://%s:%s/api" % (server, port)
    endpoints = {
        'tasks': '%s/tasks/' % base,
        'mon': '%s/mon/' % base,
        'rgw': '%s/rgw/' % base,
        'calamari': '%s/calamari/' % base,
        'osd': '%s/tasks/' % base,
    }
    url = base
    if endpoint:
        url = endpoints[endpoint]

    if args:
        for part in args:
            url = os.path.join(url, part)
    return url


def which(executable):
    """
    Locate in known system $PATH locations where an executable might exist.
    This will mean that non-system $PATH locations (like virtualenv paths) will
    be fully ignored.
    """
    locations = (
        '/usr/local/bin',
        '/bin',
        '/usr/bin',
        '/usr/local/sbin',
        '/usr/sbin',
        '/sbin',
    )

    for location in locations:
        executable_path = os.path.join(location, executable)
        if os.path.exists(executable_path):
            return executable_path


def get_playbook_path():
    """
    Try to determine where does the ansible playbook lives. It does this by
    looking into an environment variable first which takes precedence (for
    now).
    """
    try:
        playbook_path = os.environ['MARINER_PLAYBOOK']
    except KeyError:
        # TODO: Fallback nicely into looking maybe in some directory that is
        # included with the mariner application or a well know path defined by
        # the packaging of said playbooks
        logger.warning('"MARINER_PLAYBOOK" environment variable is not defined')
        playbook_path = '/tmp/ceph-ansible/'

    if os.path.isfile(playbook_path):
        # we have what should be a YAML
        return playbook_path
    else:
        # assume the site.yml file living in this directory
        return os.path.join(playbook_path, 'site.yml')

    # TODO: error here in a way that a controller can handle it and report back
