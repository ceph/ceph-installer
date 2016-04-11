from ceph_installer.controllers import osd


class TestOSDController(object):

    def setup(self):
        data = dict(
            host="node1",
            fsid="1720107309134",
            devices={'/dev/sdb': '/dev/sdc'},
            monitors=[{"host": "mon1.host", "address": "10.0.0.1"}],
            journal_size=100,
            public_network="0.0.0.0/24",
        )
        self.configure_data = data

    def test_index_get(self, session):
        result = session.app.get("/api/osd/")
        assert result.status_int == 200

    def test_configure_missing_fields(self, session):
        data = dict()
        result = session.app.post_json("/api/osd/configure/", params=data,
                                       expect_errors=True)
        assert result.status_int == 400

    def test_configure_get(self, session):
        result = session.app.get("/api/osd/configure", expect_errors=True)
        assert result.status_int == 405

    def test_configure_devices_is_wrong_type(self, session, monkeypatch):
        monkeypatch.setattr(osd.call_ansible, 'apply_async', lambda args, kwargs: None)
        data = self.configure_data.copy()
        data['devices'] = "/dev/sdb"
        result = session.app.post_json("/api/osd/configure/", params=data,
                                       expect_errors=True)
        assert result.status_int == 400
        message = result.json["message"]
        assert 'devices' in message
        assert 'not of type dictionary' in message

    def test_configure_devices_is_wrong_type_in_key(self, session, monkeypatch):
        monkeypatch.setattr(osd.call_ansible, 'apply_async', lambda args, kwargs: None)
        data = self.configure_data.copy()
        data['devices'] = {"/dev/sdb": 1}
        result = session.app.post_json("/api/osd/configure/", params=data,
                                       expect_errors=True)
        assert result.status_int == 400
        message = result.json["message"]
        assert '/dev/sdb' in message
        assert message.endswith(
                '1 failed validation, not of type string'
        )

    def test_configure_invalid_field(self, session):
        data = self.configure_data.copy()
        data["bogus"] = "invalid"
        result = session.app.post_json("/api/osd/configure/", params=data,
                                       expect_errors=True)
        assert result.status_int == 400

    def test_configure_success(self, session, monkeypatch):
        monkeypatch.setattr(osd.call_ansible, 'apply_async', lambda args, kwargs: None)
        result = session.app.post_json("/api/osd/configure/", params=self.configure_data)
        assert result.status_int == 200
        assert result.json['endpoint'] == '/api/osd/configure/'
        assert result.json['identifier'] is not None

    def test_configure_monitor_hosts_interface(self, session, monkeypatch):
        self.configure_data['monitors'] = [{"host": "mon1.host", "interface": "eth1"}]

        def check(args, kwargs):
            inventory = args[0]
            assert "mon1.host monitor_interface=eth1" in inventory[1][1]

        monkeypatch.setattr(osd.call_ansible, 'apply_async', check)
        result = session.app.post_json("/api/osd/configure/", params=self.configure_data)
        assert result.status_int == 200

    def test_configure_monitor_hosts_address(self, session, monkeypatch):
        def check(args, kwargs):
            inventory = args[0]
            assert "mon1.host monitor_address=10.0.0.1" in inventory[1][1]

        monkeypatch.setattr(osd.call_ansible, 'apply_async', check)
        result = session.app.post_json("/api/osd/configure/", params=self.configure_data)
        assert result.status_int == 200

    def test_configure_redhat_storage(self, session, monkeypatch):
        def check(args, kwargs):
            extra_vars = kwargs["extra_vars"]
            assert "redhat_storage" not in extra_vars
            assert "ceph_stable_rh_storage" in extra_vars

        data = self.configure_data.copy()
        data["redhat_storage"] = True
        monkeypatch.setattr(osd.call_ansible, 'apply_async', check)
        result = session.app.post_json("/api/osd/configure/", params=data)
        assert result.status_int == 200

    def test_configure_playbook(self, session, monkeypatch):
        def check(args, kwargs):
            assert "osd-configure.yml" in kwargs["playbook"]

        monkeypatch.setattr(osd.call_ansible, 'apply_async', check)
        result = session.app.post_json("/api/osd/configure/", params=self.configure_data)
        assert result.status_int == 200

    def test_configure_with_conf(self, session, monkeypatch):
        monkeypatch.setattr(osd.call_ansible, 'apply_async', lambda args, kwargs: None)
        self.configure_data['conf'] = {"global": {"auth supported": "cephx"}}
        result = session.app.post_json("/api/osd/configure/", params=self.configure_data)
        assert result.json['endpoint'] == '/api/osd/configure/'
        assert result.json['identifier'] is not None

    def test_configure_with_invalid_conf(self, session, monkeypatch):
        monkeypatch.setattr(osd.call_ansible, 'apply_async', lambda args, kwargs: None)
        self.configure_data['conf'] = {"global": {"auth supported": "cephx"}, "monn": 1}
        result = session.app.post_json("/api/osd/configure/", params=self.configure_data,
                                       expect_errors=True)
        assert result.status_int == 400
        assert "unexpected item in data" in result.json["message"]

    def test_configure_monitor_name_is_set(self, session, monkeypatch, argtest):
        monkeypatch.setattr(
            osd.call_ansible, 'apply_async', argtest)
        self.configure_data['host'] = "mon1.host"
        session.app.post_json("/api/osd/configure/", params=self.configure_data)
        kwargs = argtest.kwargs['kwargs']
        assert kwargs['extra_vars']['monitor_name'] == "mon1.host"

    def test_configure_monitor_name_is_not_set(self, session, monkeypatch, argtest):
        monkeypatch.setattr(
            osd.call_ansible, 'apply_async', argtest)
        session.app.post_json("/api/osd/configure/", params=self.configure_data)
        kwargs = argtest.kwargs['kwargs']
        assert "monitor_name" not in kwargs['extra_vars']

    def test_configure_with_cluster_name(self, session, monkeypatch, argtest):
        monkeypatch.setattr(
            osd.call_ansible, 'apply_async', argtest)
        self.configure_data['cluster_name'] = "lol"
        session.app.post_json("/api/osd/configure/", params=self.configure_data)
        extra_vars = argtest.kwargs['kwargs']['extra_vars']
        assert "cluster" in extra_vars
        assert "cluster_name" not in extra_vars
        assert extra_vars["cluster"] == "lol"


class TestOsdVerbose(object):

    def setup(self):
        self.configure_data = dict(
            verbose=True,
            host="node1",
            fsid="1720107309134",
            devices={'/dev/sdb': '/dev/sdc'},
            monitors=[{"host": "mon1.host", "interface": "eth1"}],
            journal_size=100,
            public_network="0.0.0.0/24",
        )

    def test_install_verbose(self, session, monkeypatch, argtest):
        monkeypatch.setattr(
            osd.call_ansible, 'apply_async', argtest)
        data = {"hosts": ["node1"], "verbose": True}
        session.app.post_json("/api/osd/install/", params=data)
        kwargs = argtest.kwargs['kwargs']
        assert kwargs['verbose'] is True

    def test_install_non_verbose(self, session, monkeypatch, argtest):
        monkeypatch.setattr(
            osd.call_ansible, 'apply_async', argtest)
        data = {"hosts": ["node1"]}
        session.app.post_json("/api/osd/install/", params=data)
        kwargs = argtest.kwargs['kwargs']
        assert kwargs['verbose'] is False

    def test_configure_verbose(self, session, monkeypatch, argtest):
        monkeypatch.setattr(
            osd.call_ansible, 'apply_async', argtest)
        session.app.post_json("/api/osd/configure/", params=self.configure_data)
        kwargs = argtest.kwargs['kwargs']
        assert kwargs['verbose'] is True

    def test_configure_non_verbose(self, session, monkeypatch, argtest):
        monkeypatch.setattr(
            osd.call_ansible, 'apply_async', argtest)
        self.configure_data.pop('verbose')
        session.app.post_json("/api/osd/configure/", params=self.configure_data)
        kwargs = argtest.kwargs['kwargs']
        assert kwargs['verbose'] is False
