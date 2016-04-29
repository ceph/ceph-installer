import os
from ceph_installer.controllers import setup


class TestSetupController(object):

    def test_index_generates_a_script(self, session):
        result = session.app.get('/setup/')
        assert '#!/bin/bash' in result.body

    def test_index_adds_the_right_endpoint_to_the_script(self, session):
        result = session.app.get('/setup/')
        assert 'http://localhost/setup/key/' in result.body

    def test_creates_the_ssh_directory(self, session, tmpdir, monkeypatch):
        rsa_path = os.path.join(str(tmpdir), '.ssh/id_rsa')
        monkeypatch.setattr(setup.os.path, 'expanduser', lambda x: rsa_path)
        session.app.get('/setup/key/')
        assert os.path.isdir(os.path.join(str(tmpdir), '.ssh'))

    def test_creates_the_ssh_key(self, session, tmpdir, monkeypatch):
        rsa_path = os.path.join(str(tmpdir), '.ssh/id_rsa')
        monkeypatch.setattr(setup.os.path, 'expanduser', lambda x: rsa_path)
        session.app.get('/setup/key/')
        assert os.path.isfile(rsa_path)

    def test_errors_when_subprocess_fails(self, session, tmpdir, monkeypatch):
        rsa_path = os.path.join(str(tmpdir), 'id_rsa')
        monkeypatch.setattr(setup.os.path, 'expanduser', lambda x: rsa_path)
        monkeypatch.setattr(
            setup.process,
            'run',
            lambda x, send_input: ('', '', 123))
        result = session.app.get('/setup/key/', expect_errors=True)
        assert result.status_int == 500

    def test_error_message_from_subprocess_failure(self, session, tmpdir, monkeypatch):
        rsa_path = os.path.join(str(tmpdir), 'id_rsa')
        monkeypatch.setattr(setup.os.path, 'expanduser', lambda x: rsa_path)
        monkeypatch.setattr(
            setup.process,
            'run',
            lambda x, send_input: ('', 'no can ssh', 123))
        result = session.app.get('/setup/key/', expect_errors=True)
        assert result.json['message'] == 'stdout: "" stderr: "no can ssh"'
