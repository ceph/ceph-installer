from notario.validators import types
from notario.decorators import optional


def list_of_hosts(value):
    assert isinstance(value, list), "requires format: ['host1', 'host2']"


def list_of_devices(value):
    assert isinstance(value, list), "requires format: ['/dev/sdb', '/dev/sdc']"


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
)

mon_configure_schema = (
    ("fsid", types.string),
    ("host", types.string),
    ("monitor_interface", types.string),
    (optional("monitor_secret"), types.string),
    (optional("monitors"), list_of_monitors),
    (optional("redhat_storage"), types.boolean),
)

osd_configure_schema = (
    ("cluster_network", types.string),
    ("devices", list_of_devices),
    ("fsid", types.string),
    ("host", types.string),
    ("journal_collocation", types.boolean),
    ("journal_size", types.integer),
    ("monitor_hosts", list_of_hosts),
    ("monitor_interface", types.string),
    ("public_network", types.string),
    (optional("redhat_storage"), types.boolean),
)
