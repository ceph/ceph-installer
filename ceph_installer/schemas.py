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
    error_msg = 'not of type dictionary or list'
    if isinstance(_object, dict):
        v = recursive.AllObjects((types.string, types.string))
        # this is truly unfortunate but we don't have access to the 'tree' here
        # (the tree is the path to get to the failing key. We settle by just being
        # able to report nicely.
        v(_object, [])
        return

    try:
        assert isinstance(_object, list)
    except AssertionError:
        if args:
            raise Invalid('dict type', pair='value', msg=None, reason=error_msg, *args)
        raise



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


rgw_configure_schema = (
    (optional("cluster_name"), types.string),
    (optional("cluster_network"), types.string),
    (optional("conf"), conf),
    (optional("email_address"), types.string),
    ("fsid", types.string),
    ("host", types.string),
    ("public_network", types.string),
    (optional("radosgw_civetweb_bind_ip"), types.string),
    (optional("radosgw_civetweb_num_threads"), types.integer),
    (optional("radosgw_civetweb_port"), types.integer),
    (optional("radosgw_dns_name"), types.string),
    (optional("radosgw_dns_s3website_name"), types.string),
    (optional("radosgw_keystone"), types.boolean),
    (optional("radosgw_keystone_accepted_roles"), types.array),
    (optional("radosgw_keystone_admin_domain"), types.string),
    (optional("radosgw_keystone_admin_password"), types.string),
    (optional("radosgw_keystone_admin_tenant"), types.string),
    (optional("radosgw_keystone_admin_token"), types.string),
    (optional("radosgw_keystone_admin_user"), types.string),
    (optional("radosgw_keystone_api_version"), types.integer),
    (optional("radosgw_keystone_auth_method"), types.string),
    (optional("radosgw_keystone_revocation_internal"), types.integer),
    (optional("radosgw_keystone_ssl"), types.boolean),
    (optional("radosgw_keystone_token_cache_size"), types.integer),
    (optional("radosgw_keystone_url"), types.string),
    (optional("radosgw_nss_db_path"), types.string),
    (optional("radosgw_resolve_cname"), types.boolean),
    (optional("radosgw_s3_auth_use_keystone"), types.boolean),
    (optional("radosgw_static_website"), types.boolean),
    (optional("radosgw_usage_log"), types.boolean),
    (optional("radosgw_usage_log_flush_threshold"), types.integer),
    (optional("radosgw_usage_log_tick_interval"), types.integer),
    (optional("radosgw_usage_max_shards"), types.integer),
    (optional("radosgw_usage_max_user_shards"), types.integer),
    (optional("redhat_storage"), types.boolean),
    (optional("redhat_use_cdn"), types.boolean),
    (optional("verbose"), types.boolean),
)
