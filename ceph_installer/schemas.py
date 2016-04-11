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
    msg = 'requires format: [{"host": "mon1.host", "interface": "eth1"},{"host": "mon2.host", "address": "10.0.0.1"}]'
    assert isinstance(value, list), msg
    msg = 'address or interface is required for monitor lists: [{"host": "mon1", "interface": "eth1", {"host": "mon2", "address": "10.0.0.1"}]'
    for monitor in value:
        assert isinstance(monitor, dict), msg
        assert "host" in monitor, msg
        try:
            assert "interface" in monitor, msg
        except AssertionError:
            assert "address" in monitor, msg


conf = (
    (optional("global"), types.dictionary),
    (optional("mds"), types.dictionary),
    (optional("mon"), types.dictionary),
    (optional("osd"), types.dictionary),
    (optional("rgw"), types.dictionary),
)

install_schema = (
    ("hosts", list_of_hosts),
    (optional("redhat_storage"), types.boolean),
    (optional("redhat_use_cdn"), types.boolean),
    (optional("verbose"), types.boolean),
)

agent_install_schema = (
    ("hosts", list_of_hosts),
    (optional("master"), types.string),
    (optional("verbose"), types.boolean),
)

mon_install_schema = (
    (optional("calamari"), types.boolean),
    ("hosts", list_of_hosts),
    (optional("redhat_storage"), types.boolean),
    (optional("redhat_use_cdn"), types.boolean),
    (optional("verbose"), types.boolean),
)

mon_configure_schema = (
    (optional("address"), types.string),
    (optional("calamari"), types.boolean),
    (optional("cluster_name"), types.string),
    (optional("cluster_network"), types.string),
    (optional("conf"), conf),
    ("fsid", types.string),
    ("host", types.string),
    (optional("interface"), types.string),
    ("monitor_secret", types.string),
    (optional("monitors"), list_of_monitors),
    ("public_network", types.string),
    (optional("redhat_storage"), types.boolean),
    (optional("verbose"), types.boolean),
)

osd_configure_schema = (
    (optional("cluster_name"), types.string),
    (optional("cluster_network"), types.string),
    (optional("conf"), conf),
    ("devices", devices_object),
    ("fsid", types.string),
    ("host", types.string),
    ("journal_size", types.integer),
    ("monitors", list_of_monitors),
    ("public_network", types.string),
    (optional("redhat_storage"), types.boolean),
    (optional("verbose"), types.boolean),
)
