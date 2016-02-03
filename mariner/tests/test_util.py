import pecan
import os

from mariner import util


class TestGenerateInventoryFile(object):

    def test_single_host(session, tmpdir):
        pecan.conf.inventory_root_path = str(tmpdir)
        result = util.generate_inventory_file("mons", "google.com", "uuid")
        with open(result, 'r') as f:
            data = [line.strip() for line in f.readlines()]
            assert "[mons]" in data
            assert "google.com" in data

    def test_correct_filename(session, tmpdir):
        pecan.conf.inventory_root_path = str(tmpdir)
        result = util.generate_inventory_file("mons", "google.com", "uuid")
        assert "hosts_uuid" in result

    def test_multiple_hosts(session, tmpdir):
        pecan.conf.inventory_root_path = str(tmpdir)
        hosts = ['google.com', 'redhat.com']
        result = util.generate_inventory_file("mons", hosts, "uuid")
        with open(result, 'r') as f:
            data = [line.strip() for line in f.readlines()]
            assert "[mons]" in data
            assert "google.com" in data
            assert "redhat.com" in data

    def test_file_path(session, tmpdir):
        pecan.conf.inventory_root_path = str(tmpdir)
        result = util.generate_inventory_file("mons", "google.com", "uuid")
        assert result == os.path.join(str(tmpdir), "hosts_uuid")
