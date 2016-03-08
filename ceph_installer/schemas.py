from notario.validators import types, recursive
from notario.utils import forced_leaf_validator
from notario.exceptions import Invalid
from notario.decorators import optional


def list_of_hosts(value):
    assert isinstance(value, list), "requires format: ['host1', 'host2']"


def list_of_devices(value):
    assert isinstance(value, list), "requires format: ['/dev/sdb', '/dev/sdc']"


@forced_leaf_validator
def devices_object(_object, *args):
    error_msg = 'not of type dictionary'
    try:
        assert isinstance(_object, dict)
    except AssertionError:
        if args:
            raise Invalid('dict type', pair='value', msg=None, reason=error_msg, *args)
        raise

    v = recursive.AllObjects((types.string, types.string))
    # this is truly unfortunate but we don't have access to the 'tree' here
    # (the tree is the path to get to the failing key. We settle by just being
    # able to report nicely.
    v(_object, [])


def list_of_monitors(value):
    msg = "requires format: [{'host': 'mon1.host', 'interface': 'eth1'},{'host': 'mon2.host', 'interface': 'enp0s8'}]"
    assert isinstance(value, list), msg
    for monitor in value:
        assert isinstance(monitor, dict), msg
        assert "host" in monitor, msg
        assert "interface" in monitor, msg


install_schema = (
    ("hosts", list_of_hosts),
    (optional("redhat_storage"), types.boolean),
    (optional("redhat_use_cdn"), types.boolean),
    (optional("verbose"), types.boolean),
)

agent_install_schema = (
    ("hosts", list_of_hosts),
    (optional("master"), types.string),
)

mon_install_schema = (
    (optional("calamari"), types.boolean),
    ("hosts", list_of_hosts),
    (optional("redhat_storage"), types.boolean),
    (optional("redhat_use_cdn"), types.boolean),
)

mon_configure_schema = (
    (optional("calamari"), types.boolean),
    (optional("cluster_network"), types.string),
    ("fsid", types.string),
    ("host", types.string),
    ("monitor_interface", types.string),
    ("monitor_secret", types.string),
    (optional("monitors"), list_of_monitors),
    ("public_network", types.string),
    (optional("redhat_storage"), types.boolean),
    (optional("verbose"), types.boolean),
)

osd_configure_schema = (
    (optional("cluster_network"), types.string),
    ("devices", devices_object),
    ("fsid", types.string),
    ("host", types.string),
    ("journal_size", types.integer),
    ("monitors", list_of_monitors),
    ("public_network", types.string),
    (optional("redhat_storage"), types.boolean),
    (optional("verbose"), types.boolean),
)
