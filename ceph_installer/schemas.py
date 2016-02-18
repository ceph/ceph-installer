from notario.validators import types
from notario.decorators import optional


def list_of_hosts(value):
    assert isinstance(value, list), "requires format: ['host1', 'host2']"


def list_of_devices(value):
    assert isinstance(value, list), "requires format: ['/dev/sdb', '/dev/sdc']"


install_schema = (
    ("hosts", list_of_hosts),
    (optional("redhat_storage"), types.boolean),
)

mon_configure_schema = (
    ("fsid", types.string),
    ("host", types.string),
    ("monitor_interface", types.string),
    (optional("monitor_secret"), types.string),
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
    ("public_network", types.string),
    (optional("redhat_storage"), types.boolean),
)
