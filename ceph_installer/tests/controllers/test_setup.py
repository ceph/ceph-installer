import os
from ceph_installer.controllers import setup


class TestSetupController(object):

    def test_index_generates_a_script(self, session):
        result = session.app.get('/setup/')
        assert '#!/bin/bash' in result.body

    def test_index_adds_the_right_endpoint_to_the_script(self, session):
        result = session.app.get('/setup/')
        assert 'http://localhost/setup/key/' in result.body

    def test_missing_ssh_directory(self, session, tmpdir, monkeypatch):
        rsa_path = os.path.join(str(tmpdir), '.ssh/id_rsa')
        monkeypatch.setattr(setup.os.path, 'expanduser', lambda x: rsa_path)
        result = session.app.get('/setup/key/', expect_errors=True)
        assert result.status_int == 500
        assert result.json['message'].startswith('.ssh directory not found')

    def test_missing_ssh_key(self, session, tmpdir, monkeypatch):
        tmpdir.mkdir('.ssh')
        rsa_path = os.path.join(str(tmpdir), '.ssh/id_rsa')
        monkeypatch.setattr(setup.os.path, 'expanduser', lambda x: rsa_path)
        result = session.app.get('/setup/key/', expect_errors=True)
        assert result.status_int == 500
        assert result.json['message'].startswith('expected public key not found')
