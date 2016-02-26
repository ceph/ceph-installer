import os
from ceph_installer.controllers import setup


class TestSetupController(object):

    def setup(self):
        self.headers = {
            'REMOTE_ADDR': 'localhost',
            'HTTP_X_FORWARDED_FOR': '0.0.0.0'
        }

    def test_index_generates_a_script(self, session):
        result = session.app.get('/setup/')
        assert '#!/bin/bash' in result.body

    def test_index_adds_the_right_endpoint_to_the_script(self, session):
        result = session.app.get('/setup/')
        assert 'http://localhost/setup/key/' in result.body

    def test_creates_the_ssh_directory(self, session, tmpdir, monkeypatch):
        rsa_path = os.path.join(str(tmpdir), '.ssh/id_rsa')
        monkeypatch.setattr(setup.os.path, 'expanduser', lambda x: rsa_path)
        session.app.get('/setup/key/', headers=self.headers)
        assert os.path.isdir(os.path.join(str(tmpdir), '.ssh'))

    def test_creates_the_ssh_key(self, session, tmpdir, monkeypatch):
        rsa_path = os.path.join(str(tmpdir), '.ssh/id_rsa')
        monkeypatch.setattr(setup.os.path, 'expanduser', lambda x: rsa_path)
        session.app.get('/setup/key/', headers=self.headers)
        assert os.path.isfile(rsa_path)

    def test_creates_the_know_hosts(self, session, tmpdir, monkeypatch):
        hosts_path = os.path.join(str(tmpdir), '.ssh/known_hosts')
        monkeypatch.setattr(setup.os.path, 'expanduser', lambda x: hosts_path)
        session.app.get('/setup/key/', headers=self.headers)
        assert os.path.isfile(hosts_path)
        assert open(hosts_path).readlines()[-1].startswith('localhost ssh-rsa')

    def test_errors_when_subprocess_fails(self, session, tmpdir, monkeypatch):
        rsa_path = os.path.join(str(tmpdir), 'id_rsa')
        monkeypatch.setattr(setup.os.path, 'expanduser', lambda x: rsa_path)
        monkeypatch.setattr(
            setup.process,
            'run',
            lambda x, send_input: ('', '', 123))
        result = session.app.get('/setup/key/', headers=self.headers, expect_errors=True)
        assert result.status_int == 500

    def test_error_message_from_subprocess_failure(self, session, tmpdir, monkeypatch):
        rsa_path = os.path.join(str(tmpdir), 'id_rsa')
        monkeypatch.setattr(setup.os.path, 'expanduser', lambda x: rsa_path)
        monkeypatch.setattr(
            setup.process,
            'run',
            lambda x, send_input: ('', 'no can ssh', 123))
        result = session.app.get('/setup/key/', headers=self.headers, expect_errors=True)
        assert result.json['message'] == 'no can ssh'
