import errno
import os
import pecan
import tempfile
import logging
from StringIO import StringIO


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
        playbook_path = os.environ['CEPH_PLAYBOOK']
    except KeyError:
        # TODO: Fallback nicely into looking maybe in some directory that is
        # included with the ceph_installer application or a well know path defined by
        # the packaging of said playbooks
        logger.warning('"CEPH_PLAYBOOK" environment variable is not defined')
        playbook_path = '/tmp/ceph-ansible/'

    if os.path.isfile(playbook_path):
        # we have what should be a YAML
        return playbook_path
    else:
        # assume the site.yml file living in this directory
        return os.path.join(playbook_path, 'site.yml')

    # TODO: error here in a way that a controller can handle it and report back


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

        >>> get_endpoint('http://localhost:8080/some/endpoint', 'api', 'setup')
        'http://localhost:8080/api/setup/'

    ``request_url``: A string representing the full URL like ``http://api.example.com/api/``.
    """
    url = '/'.join(request_url.split('/')[:3])
    if args:
        for part in args:
            url = os.path.join(url, part)
    if not url.endswith('/'):
        return "%s/" % url
    return url


def make_setup_script(url):
    """
    Create a setup script. Done dynamically due to the need of identifying the
    correct url used to request this service. The scrip will use this URL to
    properly create the right location for the serving of the public ssh key.
    """
    ssh_key_address = get_endpoint(url, 'setup', 'key')
    bash = """#!/bin/bash -x -e
if [[ $EUID -ne 0 ]]; then
  echo "You must be a root user or execute this script with sudo" 2>&1
  exit 1
fi

echo "--> creating new user with disabled password: ansible"
useradd ansible
passwd -d ansible

echo "--> adding provisioning key to the ansible authorized_keys"
curl -s -L -o ansible.pub {ssh_key_address}
mkdir -p /home/ansible/.ssh
cat ansible.pub >> /home/ansible/.ssh/authorized_keys
chown -R ansible:ansible /home/ansible/.ssh

echo "--> ensuring that ansible user will be able to sudo"
echo "ansible ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/ansible > /dev/null

echo "--> ensuring ansible user does not require a tty"
echo 'Defaults:ansible !requiretty' | sudo tee /etc/sudoers.d/ansible > /dev/null
"""
    script = StringIO()
    script.write(
        bash.format(
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

    return extra_vars
