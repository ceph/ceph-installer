import os
import pecan
import tempfile


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
    Puts together the API url for mita, so that we can talk to it. Optionally, the endpoint
    argument allows to return the correct url for specific needs. For example, to create a node:

        http://0.0.0.0/api/nodes/

    """
    server = pecan.conf['server']['host']
    port = pecan.conf['server']['port']
    base = "http://%s:%s/api" % (server, port)
    endpoints = {
        'nodes': '%s/nodes/' % base,
    }
    url = base
    if endpoint:
        url = endpoints[endpoint]

    if args:
        for part in args:
            url = os.path.join(url, part)
    return url


def which(executable):
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
