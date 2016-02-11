
class TestCalamariController(object):

    def test_index_get(self, session):
        result = session.app.get("/api/calamari/")
        assert result.status_int == 200
