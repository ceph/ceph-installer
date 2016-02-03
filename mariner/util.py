import os
import pecan


def generate_inventory_file(group_name, hosts, task_uuid):
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
    inventory_root = pecan.conf.inventory_root_path
    inventory_path = os.path.join(inventory_root, "hosts_{0}".format(task_uuid))
    with open(inventory_path, "w") as f:
        f.write(result_str)
    return inventory_path
