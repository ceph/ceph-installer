from datetime import datetime
from uuid import uuid4

from mariner.models import Task

class TestTasksController(object):

    def create_task(self, **kw):
        Task(
            identifier=kw.get('identifier', str(uuid4())),
            endpoint='/api/rgw/',
            command='ansible-playbook -i "rgw.example.com," playbook.yml',
            stderr='',
            stdout='',
            started=kw.get('started', datetime.utcnow()),
            ended=kw.get('ended', datetime.utcnow()),
            succeeded = True
            )

    def test_index_get_no_tasks(self, session):
        result = session.app.get("/api/tasks/")
        assert result.json == []

    def test_index_get_single_task(self, session):
        self.create_task()
        session.commit()
        result = session.app.get("/api/tasks/")
        assert len(result.json) == 1

    def test_index_get_single_task_identifier(self, session):
        self.create_task(identifier='uuid-1')
        session.commit()
        result = session.app.get("/api/tasks/")
        assert result.json[0]['identifier'] == 'uuid-1'

    def test_index_get_single_task_endpoint(self, session):
        self.create_task()
        session.commit()
        result = session.app.get("/api/tasks/")
        assert result.json[0]['endpoint'] == '/api/rgw/'

    def test_index_get_single_task_command(self, session):
        self.create_task()
        session.commit()
        result = session.app.get("/api/tasks/")
        assert result.json[0]['command'] =='ansible-playbook -i "rgw.example.com," playbook.yml'

    def test_index_get_single_task_stdout(self, session):
        self.create_task()
        session.commit()
        result = session.app.get("/api/tasks/")
        assert result.json[0]['stdout'] == ''

    def test_index_get_single_task_stderr(self, session):
        self.create_task()
        session.commit()
        result = session.app.get("/api/tasks/")
        assert result.json[0]['stderr'] == ''

    def test_index_get_single_task_started(self, session):
        started = datetime.utcnow()
        self.create_task(started=started)
        session.commit()
        result = session.app.get("/api/tasks/")
        assert result.json[0]['started'] == started.isoformat().replace('T', ' ')

    def test_index_get_single_task_ended(self, session):
        ended = datetime.utcnow()
        self.create_task(ended=ended)
        session.commit()
        result = session.app.get("/api/tasks/")
        assert result.json[0]['ended'] == ended.isoformat().replace('T', ' ')

    def test_index_get_single_task_succeeded(self, session):
        self.create_task()
        session.commit()
        result = session.app.get("/api/tasks/")
        assert result.json[0]['succeeded'] is True
