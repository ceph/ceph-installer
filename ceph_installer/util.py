import errno
import os
import pecan
import tempfile
import logging
from StringIO import StringIO
from ceph_installer import templates


logger = logging.getLogger(__name__)


def generate_inventory_file(inventory, task_uuid, tmp_dir=None):
    """
    Generates a host file to use with an ansible-playbook call.

    The first argument is a list of tuples that contain the group name as
    the first item in the tuple and a list of hostnames in the second.

    For example:

        [('mons', ['mon.host']), ('osds', ['osd1.host', 'osd1.host'])]
    """
    result = []
    for section in inventory:
        group_name = section[0]
        hosts = section[1]
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


def parse_monitors(monitors):
    """
    Given a list of dictionaries, returns a list of hosts that
    can be used in an ansible inventory. These host lines can include
    host variables as well.

    For example, monitors in this format:

        [
            {"host": "mon0.host", "interface": "eth0"},
            {"host": "mon1.host", "interface": "enp0s8"},
        ]

    Would return the following:

        ["mon0.host monitor_interface=eth0", "mon1.host monitor_interface=enp0s8"]
    """
    hosts = []
    var_map = dict(
        interface="monitor_interface",
    )
    for mon in monitors:
        host = []
        host.append(mon["host"])
        for k, v in var_map.iteritems():
            if k in mon:
                host.append("{}={}".format(v, mon[k]))
        hosts.append(" ".join(host))

    return hosts


def mkdir(path, exist_ok=True, mode=0755):
    """
    Create a directory if it already exists do not error. Anything else should
    be treated as an error condition.
    """
    try:
        os.makedirs(path, mode=mode)
    except OSError as exc:  # Python >2.5
        if not exist_ok:
            raise
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def api_endpoint(endpoint=None, *args):
    """
    Puts together the API url for ceph_installer, so that we can talk to it. Optionally, the endpoint
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
        'osd': '%s/osd/' % base,
        'agent': '%s/agent/' % base,
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


def get_ceph_ansible_path():
    """
    Try to determine where does the ceph-ansible repo lives. It does this by
    looking into an environment variable first which takes precedence (for
    now).
    """
    try:
        repo_path = os.environ['CEPH_ANSIBLE_PATH']
    except KeyError:
        # TODO: Fallback nicely into looking maybe in some directory that is
        # included with the ceph_installer application or a well know path defined by
        # the packaging of said playbooks
        logger.warning('"CEPH_ANSIBLE_PATH" environment variable is not defined')
        repo_path = '/usr/share/ceph-ansible'

    return repo_path


def get_endpoint(request_url, *args):
    """
    Given a request URL, attempt to determine the full address to the `/setup/`
    endpoint so that we can re-use this when crafting the script.

    This service might not be reached at the same address as the configuration
    states so we try to match the request to ensure a subsequent request that
    can capture stdout/stderr will be correct.

    The ``request_url`` argument is required, and used to infer the base url
    this service was accessed from. All args would then be used to append to
    the main url::

        >>> get_endpoint('http://localhost:8181/some/endpoint', 'api', 'setup')
        'http://localhost:8181/api/setup/'

    ``request_url``: A string representing the full URL like ``http://api.example.com/api/``.
    """
    url = '/'.join(request_url.split('/')[:3])
    if args:
        for part in args:
            url = os.path.join(url, part)
    if not url.endswith('/'):
        return "%s/" % url
    return url


def make_agent_script(url, target_host):
    """
    Create the agent setup script. This is very similar to the
    ``make_setup_script`` with the difference being a trigger to install and
    configure the agent after the provisioning user has been created.
    """
    template = templates.setup_script + templates.agent_script
    ssh_key_address = get_endpoint(url, 'setup', 'key')
    agent_endpoint = get_endpoint(url, 'api', 'agent')
    script = StringIO()
    script.write(
        template.format(
            ssh_key_address=ssh_key_address,
            target_host=target_host,
            agent_endpoint=agent_endpoint,
        )
    )
    script.seek(0)
    return script


def make_setup_script(url):
    """
    Create a setup script. Done dynamically due to the need of identifying the
    correct url used to request this service. The scrip will use this URL to
    properly create the right location for the serving of the public ssh key.
    """
    ssh_key_address = get_endpoint(url, 'setup', 'key')
    script = StringIO()
    script.write(
        templates.setup_script.format(
            ssh_key_address=ssh_key_address,
        )
    )
    script.seek(0)
    return script


def get_install_extra_vars(json):
    """
    Given a request.json dictionary from an install endpoint, this
    method will generate and return a dict to be used as extra_vars
    for ceph_installer.tasks.install.
    """
    extra_vars = dict()
    redhat_storage = json.get("redhat_storage", False)
    if redhat_storage:
        extra_vars["ceph_stable_rh_storage"] = True
        extra_vars["ceph_stable_rh_storage_cdn_install"] = True
    else:
        # use the latest upstream stable version
        extra_vars["ceph_stable"] = True

    return extra_vars
