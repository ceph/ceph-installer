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
