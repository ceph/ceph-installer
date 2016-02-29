from ceph_installer.controllers import agent


class TestAgentController(object):

    def setup(self):
        self.configure_data = dict(
            monitor_secret="secret",
            public_network="0.0.0.0/24",
            host="node1",
            monitor_interface="eth0",
            fsid="1720107309134",
        )

    def test_index_get_is_allowed(self, session):
        result = session.app.get("/api/agent/", expect_errors=True)
        assert result.status_int == 200

    def test_install_get_is_not_allowed(self, session):
        result = session.app.get("/api/agent/install/", expect_errors=True)
        assert result.status_int == 405

    def test_install_incorrect_schema(self, session):
        data = dict(hosts=["google.com"], bogus="foo")
        result = session.app.post_json("/api/agent/install/", params=data,
                                       expect_errors=True)
        assert result.status_int == 400

    def test_install_works_with_right_schema(self, session, monkeypatch):
        monkeypatch.setattr(agent.call_ansible, 'apply_async', lambda args, kwargs: None)
        data = dict(hosts=["node1"])
        result = session.app.post_json("/api/agent/install/", params=data,
                                       expect_errors=True)
        assert result.json['endpoint'] == '/api/agent/install/'
        assert result.json['identifier'] is not None

