from ceph_installer.controllers import rgw


class TestRGWController(object):

    def setup(self):
        data = dict(
            host="node1",
            fsid="1720107309134",
            monitors=[{"host": "mon1.host", "address": "10.0.0.1"}],
            public_network="0.0.0.0/24",
        )
        self.configure_data = data

    def test_index_get(self, session):
        result = session.app.get("/api/rgw/")
        assert result.status_int == 200

    def test_install_hosts(self, session, monkeypatch):
        monkeypatch.setattr(rgw.call_ansible, 'apply_async', lambda args, kwargs: None)
        data = dict(hosts=["node1"])
        result = session.app.post_json("/api/rgw/install/", params=data)
        assert result.json['endpoint'] == '/api/rgw/install/'
        assert result.json['identifier'] is not None

    def test_install_missing_hosts(self, session):
        result = session.app.post_json("/api/rgw/install/", params=dict(),
                                       expect_errors=True)
        assert result.status_int == 400

    def test_install_bogus_field(self, session):
        data = dict(hosts=["google.com"], bogus="foo")
        result = session.app.post_json("/api/rgw/install/", params=data,
                                       expect_errors=True)
        assert result.status_int == 400

    def test_configure_missing_fields(self, session):
        data = dict()
        result = session.app.post_json("/api/rgw/configure/", params=data,
                                       expect_errors=True)
        assert result.status_int == 400

    def test_configure_success(self, session, monkeypatch):
        monkeypatch.setattr(rgw.call_ansible, 'apply_async', lambda args, kwargs: None)
        result = session.app.post_json("/api/rgw/configure/", params=self.configure_data)
        assert result.json['endpoint'] == '/api/rgw/configure/'
        assert result.json['identifier'] is not None
