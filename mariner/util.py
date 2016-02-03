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
