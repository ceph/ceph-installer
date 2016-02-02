
class TestTasksController(object):

    def test_index_get(self, session):
        result = session.app.get("/api/tasks/")
        assert result.status_int == 200
