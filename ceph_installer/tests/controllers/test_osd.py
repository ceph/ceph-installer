from ceph_installer.controllers import osd


class TestOSDController(object):

    def setup(self):
        self.configure_data = self.get_configure_data()

    def get_configure_data(self):
        data = dict(
            host="node1",
            monitor_interface="eth0",
            fsid="1720107309134",
            devices=['/dev/sdb'],
            monitor_hosts=["mon.host"],
            journal_collocation=True,
            journal_size=100,
            public_network="0.0.0.0/24",
            cluster_network="0.0.0.0/24",
        )
        return data

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

    def test_configure_devices_is_wrong_type(self, session):
        data = self.configure_data.copy()
        data['devices'] = "/dev/sdb"
        result = session.app.post_json("/api/osd/configure/", params=data,
                                       expect_errors=True)
        assert result.status_int == 400
        message = result.json["message"]
        assert 'devices' in message
        assert message.endswith(
            "failed validation, requires format: ['/dev/sdb', '/dev/sdc']"
        )

    def test_configure_invalid_field(self, session):
        data = self.configure_data.copy()
        data["bogus"] = "invalid"
        result = session.app.post_json("/api/osd/configure/", params=data,
                                       expect_errors=True)
        assert result.status_int == 400

    def test_configure_success(self, session, monkeypatch):
        monkeypatch.setattr(osd.call_ansible, 'apply_async', lambda args, kwargs: None)
        result = session.app.post_json("/api/osd/configure/", params=self.configure_data,
                                       expect_errors=True)
        assert result.status_int == 200
        assert result.json['endpoint'] == '/api/osd/configure/'
        assert result.json['identifier'] is not None

    def test_configure_monitor_hosts(self, session, monkeypatch):
        def check(args, kwargs):
            inventory = args[0]
            assert "mon.host" in inventory[1][1]

        monkeypatch.setattr(osd.call_ansible, 'apply_async', check)
        result = session.app.post_json("/api/osd/configure/", params=self.configure_data,
                                       expect_errors=True)
        assert result.status_int == 200

    def test_configure_redhat_storage(self, session, monkeypatch):
        def check(args, kwargs):
            extra_vars = kwargs["extra_vars"]
            assert "redhat_storage" not in extra_vars
            assert "ceph_stable_rh_storage" in extra_vars

        data = self.configure_data.copy()
        data["redhat_storage"] = True
        monkeypatch.setattr(osd.call_ansible, 'apply_async', check)
        result = session.app.post_json("/api/osd/configure/", params=data,
                                       expect_errors=True)
        assert result.status_int == 200

    def test_configure_playbook(self, session, monkeypatch):
        def check(args, kwargs):
            assert "osd-configure.yml" in kwargs["playbook"]

        monkeypatch.setattr(osd.call_ansible, 'apply_async', check)
        result = session.app.post_json("/api/osd/configure/", params=self.configure_data,
                                       expect_errors=True)
        assert result.status_int == 200
