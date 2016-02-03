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
