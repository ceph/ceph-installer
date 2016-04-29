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
    result_str = "\n".join(result) + "\n"
    # if not None the NamedTemporaryFile will be created in the given directory
    tempfile.tempdir = tmp_dir
    inventory_file = tempfile.NamedTemporaryFile(prefix="{0}_".format(task_uuid), delete=False)
    inventory_file.write(result_str)
    inventory_file.close()
    return inventory_file.name


def validate_monitors(monitors, host):
    """
    Ensures that the given host is not included in
    the monitors list. This fixes an issue with users
    trying to provide the monitor they are currently
    configuring in the list of 'monitors'.
    """
    result = []
    for mon in monitors:
        if mon["host"] == host:
            logger.warning("When configuring a mon it can not exist in the list of current monitors.")
            logger.warning("%s removed from monitors.", host)
            continue
        result.append(mon)
    return result


def parse_monitors(monitors):
    """
    Given a list of dictionaries, returns a list of hosts that
    can be used in an ansible inventory. These host lines can include
    host variables as well.

    For example, monitors in this format::

        [
            {"host": "mon0.host", "interface": "eth0"},
            {"host": "mon1.host", "interface": "enp0s8"},
        ]

    Would return the following::

        ["mon0.host monitor_interface=eth0", "mon1.host monitor_interface=enp0s8"]

    Because the API allows for both ``interface`` or ``address`` this utility
    will look for both.  Ideally, only one should be defined, but it is up to
    the client to ensure that the one that is needed is passed to the API.
    """
    hosts = []

    for mon in monitors:
        host = []
        host.append(mon["host"])

        # This is an 'either or' situation. The schema engine does not allow us
        # to play with situations that might have one key or the other. That
        # problem gets solved here by trying to use monitor_interface first and
        # then falling back to its address if defined.
        try:
            host.append("monitor_interface=%s" % mon['interface'])
        except KeyError:
            try:
                host.append("monitor_address=%s" % mon['address'])
            except KeyError:
                # do not append monitor_* and just use the host
                pass

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
    logger.info("Setting redhat_storage to %s", redhat_storage)
    use_cdn = json.get("redhat_use_cdn", True)
    logger.info("Setting redhat_use_cdn to %s", use_cdn)
    if redhat_storage:
        extra_vars["ceph_stable_rh_storage"] = True
        if not use_cdn:
            # this tells ceph-ansible to install from the
            # existing repos on the system
            extra_vars["ceph_origin"] = "distro"
        else:
            extra_vars["ceph_stable_rh_storage_cdn_install"] = True
    else:
        # use the latest upstream stable version
        extra_vars["ceph_stable"] = True
    # fetch_directory must be a writable location.
    fetch = os.path.join(os.environ['HOME'], 'fetch')
    extra_vars["fetch_directory"] = fetch

    return extra_vars


def get_osd_configure_extra_vars(json):
    """
    Given a request.json dictionary from the api/osd/configure/ endpoint,
    this method will generate and return a dict to be used as extra_vars
    for ceph_installer.tasks.install.

    This new dictionary "translates" exposed/documented keys and values to
    variables that ceph-ansible can consume correctly. That is the reason why
    some of these keys are dropped from the incoming dictionary to the outgoing
    one.
    """
    extra_vars = get_install_extra_vars(json)
    # The extra_vars dictionary gets updated here *with whatever exists in the
    # json* so any modifications must happen after this is performed to ensure
    # that changes are not overwritten.
    extra_vars.update(json)

    # enforce this option, which is the only "scenario" supported
    extra_vars['raw_multi_journal'] = True

    device_map = json["devices"]
    devices = []
    journal_devices = []

    for device, journal in device_map.items():
        devices.append(device)
        journal_devices.append(journal)

    # add the corresponding device and journal to what ceph-ansible expects
    extra_vars['devices'] = devices
    extra_vars['raw_journal_devices'] = journal_devices

    monitor_hosts = [mon['host'] for mon in json["monitors"]]
    host = json['host']
    if host in monitor_hosts:
        logger.info("The host %s is in both the OSD and MON groups.", host)
        # The role ceph-mon isn't used during on OSD configure so the
        # monitor_name variable is never set, but it needs to exist because
        # the ceph-common role will attempt to restart mons because this host
        # is both a mon and an osd.
        extra_vars['monitor_name'] = host

    if "cluster_name" in extra_vars:
        extra_vars["cluster"] = extra_vars["cluster_name"]
        del extra_vars["cluster_name"]

    # These are items that came via the JSON that should never be passed into
    # ceph-ansible because they are no longer needed
    del extra_vars['host']
    del extra_vars['monitors']
    if 'redhat_storage' in json:
        del extra_vars['redhat_storage']

    return extra_vars
