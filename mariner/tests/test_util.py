import pecan
import os

from mariner import util


class TestGenerateInventoryFile(object):

    def test_single_host(session, tmpdir):
        result = util.generate_inventory_file("mons", "google.com", "uuid", tmp_dir=str(tmpdir))
        with open(result, 'r') as f:
            data = [line.strip() for line in f.readlines()]
            assert "[mons]" in data
            assert "google.com" in data

    def test_correct_filename(session, tmpdir):
        result = util.generate_inventory_file("mons", "google.com", "uuid", tmp_dir=str(tmpdir))
        assert "uuid_" in result

    def test_multiple_hosts(session, tmpdir):
        hosts = ['google.com', 'redhat.com']
        result = util.generate_inventory_file("mons", hosts, "uuid", tmp_dir=str(tmpdir))
        with open(result, 'r') as f:
            data = [line.strip() for line in f.readlines()]
            assert "[mons]" in data
            assert "google.com" in data
            assert "redhat.com" in data

    def test_tmp_dir(session, tmpdir):
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
