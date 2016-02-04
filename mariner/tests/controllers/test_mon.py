
class TestMonController(object):

    def test_index_get(self, session):
        result = session.app.get("/api/mon/")
        assert result.status_int == 200

    def test_install_incorrect_json(self, session):
        result = session.app.post_json("/api/mon/install/", params=dict(),
                                       expect_errors=True)
        assert result.status_int == 400
