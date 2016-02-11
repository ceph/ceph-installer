
class TestRGWController(object):

    def test_index_get(self, session):
        result = session.app.get("/api/rgw/")
        assert result.status_int == 200
