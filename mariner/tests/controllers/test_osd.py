
class TestOSDController(object):

    def test_index_get(self, session):
        result = session.app.get("/api/osd/")
        assert result.status_int == 200
