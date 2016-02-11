import os

import pytest
from mariner import util


class TestGenerateInventoryFile(object):

    def test_single_host(self, tmpdir):
        result = util.generate_inventory_file("mons", "google.com", "uuid", tmp_dir=str(tmpdir))
        with open(result, 'r') as f:
            data = [line.strip() for line in f.readlines()]
            assert "[mons]" in data
            assert "google.com" in data

    def test_correct_filename(self, tmpdir):
        result = util.generate_inventory_file("mons", "google.com", "uuid", tmp_dir=str(tmpdir))
        assert "uuid_" in result

    def test_multiple_hosts(self, tmpdir):
        hosts = ['google.com', 'redhat.com']
        result = util.generate_inventory_file("mons", hosts, "uuid", tmp_dir=str(tmpdir))
        with open(result, 'r') as f:
            data = [line.strip() for line in f.readlines()]
            assert "[mons]" in data
            assert "google.com" in data
            assert "redhat.com" in data

    def test_tmp_dir(self, tmpdir):
        result = util.generate_inventory_file("mons", "google.com", "uuid", tmp_dir=str(tmpdir))
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
        assert not result

    def test_redhat_storage_is_true(self):
        data = dict(redhat_storage=True)
        result = util.get_install_extra_vars(data)
        assert "ceph_stable_rh_storage" in result
        assert "ceph_stable_rh_storage_cdn_install" in result

    def test_redhat_storage_is_false(self):
        data = dict(redhat_storage=False)
        result = util.get_install_extra_vars(data)
        assert not result
