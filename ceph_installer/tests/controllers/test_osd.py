from ceph_installer.controllers import osd


class TestOSDController(object):

    def test_index_get(self, session):
        result = session.app.get("/api/osd/")
        assert result.status_int == 200

    def test_configure_missing_fields(self, session):
        data = dict()
        result = session.app.post_json("/api/osd/configure/", params=data,
                                       expect_errors=True)
        assert result.status_int == 400

    def test_configure_success(self, session, monkeypatch):
        monkeypatch.setattr(osd.call_ansible, 'apply_async', lambda args, kwargs: None)
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
        result = session.app.post_json("/api/osd/configure/", params=data,
                                       expect_errors=True)
        assert result.status_int == 200
        assert result.json['endpoint'] == '/api/osd/configure/'
        assert result.json['identifier'] is not None
