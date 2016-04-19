# -*- coding: utf8 -*-

from ceph_installer import process


class TestMakeAnsibleCommand(object):

    def test_with_tags(self, monkeypatch):
        monkeypatch.setattr(process, 'which', lambda x: "/bin/ansible")
        result = process.make_ansible_command("/hosts", "uuid", tags="package-install")
        assert "--tags" in result
        assert "package-install" in result

    def test_with_skip_tags(self, monkeypatch):
        monkeypatch.setattr(process, 'which', lambda x: "/bin/ansible")
        result = process.make_ansible_command("/hosts", "uuid", skip_tags="package-install")
        assert "--skip-tags" in result
        assert "package-install" in result

    def test_with_extra_vars(self, monkeypatch):
        monkeypatch.setattr(process, 'which', lambda x: "/bin/ansible")
        result = process.make_ansible_command("/hosts", "uuid", extra_vars=dict(foo="bar"))
        assert '{"foo": "bar"}' in result
        assert "--extra-vars" in result

    def test_with_playbook(self, monkeypatch):
        monkeypatch.setattr(process, 'which', lambda x: "/bin/ansible")
        result = process.make_ansible_command("/hosts", "uuid", playbook="playbook.yml")
        assert "/usr/share/ceph-ansible/playbook.yml" in result


class FakePopen(object):

    def __init__(self, stdout='', stderr='', returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode

    def communicate(self, *a):
        return self.stdout, self.stderr


class TestProcess(object):

    def test_decode_unicode_on_the_fly_for_stdout(self, monkeypatch):
        monkeypatch.setattr(
            process.subprocess, 'Popen',
            lambda *a, **kw: FakePopen('£', 'stderr')
        )
        stdout, stderr, code = process.run('ls')
        assert stdout == u'\xa3'

    def test_decode_unicode_on_the_fly_for_stderr(self, monkeypatch):
        monkeypatch.setattr(
            process.subprocess, 'Popen',
            lambda *a, **kw: FakePopen('stdout', '™')
        )
        stdout, stderr, code = process.run('ls')
        assert stderr == u'\u2122'
