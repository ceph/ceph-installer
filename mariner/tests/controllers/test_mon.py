
class TestMonController(object):

    def test_index_get(self, session):
        result = session.app.get("/api/mon/")
        assert result.status_int == 200
