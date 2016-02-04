
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
