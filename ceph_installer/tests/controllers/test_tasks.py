from datetime import datetime
from uuid import uuid4

from ceph_installer.models import Task


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
            succeeded=True
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
        assert result.json[0]['command'] == 'ansible-playbook -i "rgw.example.com," playbook.yml'

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


class TestTaskController(object):

    def create_task(self, **kw):
        Task(
            identifier=kw.get('identifier', str(uuid4())),
            endpoint='/api/rgw/',
            command='ansible-playbook -i "rgw.example.com," playbook.yml',
            stderr='',
            stdout='',
            started=kw.get('started', datetime.utcnow()),
            ended=kw.get('ended', datetime.utcnow()),
            succeeded=True
        )

    def test_task_not_found(self, session):
        result = session.app.get(
            '/api/tasks/1234-asdf-1234-asdf/',
            expect_errors=True)
        assert result.status_int == 404

    def test_task_exists_with_metadata(self, session):
        identifier = '1234-asdf-1234-asdf'
        self.create_task(identifier=identifier)
        result = session.app.get('/api/tasks/1234-asdf-1234-asdf/')
        assert result.json['identifier']


class TestTaskControllerRequests(object):

    def create_task(self, **kw):

        Task(
            request=kw.get('request'),
            identifier=kw.get('identifier', '1234-asdf-1234-asdf'),
            endpoint='/api/rgw/',
            command='ansible-playbook -i "rgw.example.com," playbook.yml',
            stderr='',
            stdout='',
            started=kw.get('started', datetime.utcnow()),
            ended=kw.get('ended', datetime.utcnow()),
            succeeded=True
        )

    def test_request_is_none(self, session):
        self.create_task()
        result = session.app.get(
            '/api/tasks/1234-asdf-1234-asdf/',
            expect_errors=True)
        print result.json
        assert result.json['user_agent'] == ''
        assert result.json['http_method'] == ''
        assert result.json['request'] == ''

    def test_request_with_valid_method(self, fake, session):
        fake_request = fake(method='POST')
        self.create_task(request=fake_request)
        result = session.app.get('/api/tasks/1234-asdf-1234-asdf/')
        assert result.json['http_method'] == 'POST'

    def test_request_with_valid_body(self, fake, session):
        fake_request = fake(body='{"host": "example.com"}')
        self.create_task(request=fake_request)
        result = session.app.get('/api/tasks/1234-asdf-1234-asdf/')
        assert result.json['request'] == '{"host": "example.com"}'

    def test_request_with_valid_user_agent(self, fake, session):
        fake_request = fake(user_agent='Mozilla/5.0')
        self.create_task(request=fake_request)
        result = session.app.get('/api/tasks/1234-asdf-1234-asdf/')
        assert result.json['user_agent'] == 'Mozilla/5.0'
