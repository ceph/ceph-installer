import os

import pytest
from ceph_installer import util


class TestGenerateInventoryFile(object):

    def test_single_host(self, tmpdir):
        result = util.generate_inventory_file([("mons", "google.com")], "uuid", tmp_dir=str(tmpdir))
        with open(result, 'r') as f:
            data = [line.strip() for line in f.readlines()]
            assert "[mons]" in data
            assert "google.com" in data

    def test_correct_filename(self, tmpdir):
        result = util.generate_inventory_file([("mons", "google.com")], "uuid", tmp_dir=str(tmpdir))
        assert "uuid_" in result

    def test_multiple_hosts(self, tmpdir):
        hosts = ['google.com', 'redhat.com']
        result = util.generate_inventory_file([("mons", hosts)], "uuid", tmp_dir=str(tmpdir))
        with open(result, 'r') as f:
            data = [line.strip() for line in f.readlines()]
            assert "[mons]" in data
            assert "google.com" in data
            assert "redhat.com" in data

    def test_multiple_groups(self, tmpdir):
        hosts = ['google.com', 'redhat.com']
        inventory = [('mons', hosts), ('osds', 'osd1.host')]
        result = util.generate_inventory_file(inventory, "uuid", tmp_dir=str(tmpdir))
        with open(result, 'r') as f:
            data = [line.strip() for line in f.readlines()]
            assert "[mons]" in data
            assert "google.com" in data
            assert "redhat.com" in data
            assert "[osds]" in data
            assert "osd1.host" in data

    def test_tmp_dir(self, tmpdir):
        result = util.generate_inventory_file([("mons", "google.com")], "uuid", tmp_dir=str(tmpdir))
        assert str(tmpdir) in result


class TestGetEndpoint(object):

    def test_no_args(self):
        result = util.get_endpoint('http://example.org/some/endpoint')
        assert result == 'http://example.org/'

    def test_one_arg(self):
        result = util.get_endpoint('http://example.org/some/endpoint', 'setup')
        assert result == 'http://example.org/setup/'

    def test_no_trailing_slash(self):
        result = util.get_endpoint('http://example.org', 'setup')
        assert result == 'http://example.org/setup/'


class TestMkdir(object):

    def test_mkdir_success(self, tmpdir):
        path = os.path.join(str(tmpdir), 'mydir')
        util.mkdir(path)
        assert os.path.isdir(path) is True

    def test_mkdir_ignores_existing_dir(self, tmpdir):
        path = str(tmpdir)
        util.mkdir(path)
        assert os.path.isdir(path) is True

    def test_mkdir_does_not_ignore_existing_dir(self, tmpdir):
        path = str(tmpdir)
        with pytest.raises(OSError):
            util.mkdir(path, exist_ok=False)


class TestGetInstallExtraVars(object):

    def test_no_extra_vars(self):
        data = dict()
        result = util.get_install_extra_vars(data)
        expected = {
            'ceph_stable': True,
            'fetch_directory': os.path.join(os.environ['HOME'], 'fetch'),
        }
        assert result == expected

    def test_redhat_storage_is_true(self):
        data = dict(redhat_storage=True)
        result = util.get_install_extra_vars(data)
        assert "ceph_stable_rh_storage" in result
        assert "ceph_stable_rh_storage_cdn_install" in result

    def test_redhat_storage_is_false(self):
        data = dict(redhat_storage=False)
        result = util.get_install_extra_vars(data)
        expected = {
            'ceph_stable': True,
            'fetch_directory': os.path.join(os.environ['HOME'], 'fetch'),
        }
        assert result == expected

    def test_redhat_use_cdn_is_true(self):
        data = dict(redhat_storage=True, redhat_use_cdn=True)
        result = util.get_install_extra_vars(data)
        assert "ceph_stable_rh_storage" in result
        assert "ceph_stable_rh_storage_cdn_install" in result

    def test_redhat_use_cdn_is_false(self):
        data = dict(redhat_storage=True, redhat_use_cdn=False)
        result = util.get_install_extra_vars(data)
        assert "ceph_stable_rh_storage" in result
        assert "ceph_stable_rh_storage_cdn_install" not in result

    def test_ceph_origin_exists_when_not_using_the_cdn(self):
        data = dict(redhat_storage=True, redhat_use_cdn=False)
        result = util.get_install_extra_vars(data)
        assert "ceph_origin" in result

    def test_ceph_origin_does_not_exists_when_using_the_cdn(self):
        data = dict(redhat_storage=True, redhat_use_cdn=True)
        result = util.get_install_extra_vars(data)
        assert "ceph_origin" not in result


class TestGetOSDConfigureExtraVars(object):

    def setup(self):
        self.data = dict(
            host="node1",
            fsid="1720107309134",
            devices={'/dev/sdb': '/dev/sdc'},
            monitors=[{"host": "mon1.host", "interface": "eth1"}],
            journal_size=100,
            public_network="0.0.0.0/24",
        )

    def test_raw_multi_journal_is_set(self):
        result = util.get_osd_configure_extra_vars(self.data)
        assert "raw_multi_journal" in result

    def test_raw_journal_devices(self):
        result = util.get_osd_configure_extra_vars(self.data)
        assert "raw_journal_devices" in result
        assert result["raw_journal_devices"] == ["/dev/sdc"]

    def test_redhat_storage_not_present(self):
        data = self.data.copy()
        data["redhat_storage"] = True
        result = util.get_osd_configure_extra_vars(self.data)
        assert "redhat_storage" not in result

    def test_devices_should_be_a_list(self):
        # regression
        result = util.get_osd_configure_extra_vars(self.data)
        assert result["devices"] == ["/dev/sdb"]

    def test_monitor_name_is_set(self):
        # simulates the scenario where this host is a mon and an osd
        data = self.data.copy()
        data['host'] = "mon1.host"
        result = util.get_osd_configure_extra_vars(data)
        assert "monitor_name" in result
        assert result['monitor_name'] == "mon1.host"


class TestParseMonitors(object):

    def test_with_interface(self):
        data = [
            {"host": "mon0.host", "interface": "eth0"},
            {"host": "mon1.host", "interface": "eth1"},
        ]
        results = util.parse_monitors(data)
        assert "mon0.host monitor_interface=eth0" in results
        assert "mon1.host monitor_interface=eth1" in results

    def test_with_address(self):
        data = [
            {"host": "mon0.host", "address": "eth0"},
            {"host": "mon1.host", "address": "eth1"},
        ]
        results = util.parse_monitors(data)
        assert "mon0.host monitor_address=eth0" in results
        assert "mon1.host monitor_address=eth1" in results

    def test_one_with_no_interface(self):
        data = [
            {"host": "mon0.host"},
            {"host": "mon1.host", "interface": "eth1"},
        ]
        results = util.parse_monitors(data)
        assert "mon0.host" == results[0]
        assert "mon1.host monitor_interface=eth1" in results

    def test_invalid_extra_var(self):
        data = [
            {"host": "mon1.host", "foo": "bar"},
        ]
        results = util.parse_monitors(data)
        assert "mon1.host" == results[0]


class TestValidateMonitors(object):

    def test_host_given_as_monitor(self):
        data = [
            {"host": "mon1.host", "foo": "bar"},
        ]
        results = util.validate_monitors(data, "mon1.host")
        assert not results

    def test_host_not_given_as_monitor(self):
        data = [
            {"host": "mon1.host", "foo": "bar"},
        ]
        results = util.validate_monitors(data, "mon2.host")
        assert results == data

    def test_host_not_exact_match_in_monitors(self):
        data = [
            {"host": "mon1.host", "foo": "bar"},
        ]
        results = util.validate_monitors(data, "mon1")
        assert results == data

    def test_remove_host_from_monitors_leaving_others(self):
        data = [
            {"host": "mon1.host", "foo": "bar"},
            {"host": "mon2.host", "foo": "bar"},
        ]
        results = util.validate_monitors(data, "mon1.host")
        assert len(results) == 1
        assert results[0]['host'] == "mon2.host"
