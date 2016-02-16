from ceph_installer.controllers import mon


class TestMonController(object):

    def test_index_get(self, session):
        result = session.app.get("/api/mon/")
        assert result.status_int == 200

    def test_install_missing_hosts(self, session):
        result = session.app.post_json("/api/mon/install/", params=dict(),
                                       expect_errors=True)
        assert result.status_int == 400

    def test_install_bogus_field(self, session):
        data = dict(hosts=["google.com"], bogus="foo")
        result = session.app.post_json("/api/mon/install/", params=data,
                                       expect_errors=True)
        assert result.status_int == 400

    def test_install_hosts_not_a_list(self, session):
        data = dict(hosts="google.com")
        result = session.app.post_json("/api/mon/install/", params=data,
                                       expect_errors=True)
        assert result.status_int == 400

    def test_install_hosts(self, session, monkeypatch):
        monkeypatch.setattr(mon.call_ansible, 'apply_async', lambda args, kwargs: None)
        data = dict(hosts=["node1"])
        result = session.app.post_json("/api/mon/install/", params=data,
                                       expect_errors=True)
        assert result.json['endpoint'] == '/api/mon/install/'
        assert result.json['identifier'] is not None

    def test_configure_missing_fields(self, session):
        data = dict()
        result = session.app.post_json("/api/mon/configure/", params=data,
                                       expect_errors=True)
        assert result.status_int == 400

    def test_configure_hosts(self, session, monkeypatch):
        monkeypatch.setattr(mon.call_ansible, 'apply_async', lambda args, kwargs: None)
        data = dict(host="node1", monitor_interface="eth0", fsid="1720107309134")
        result = session.app.post_json("/api/mon/configure/", params=data,
                                       expect_errors=True)
        assert result.json['endpoint'] == '/api/mon/configure/'
        assert result.json['identifier'] is not None
