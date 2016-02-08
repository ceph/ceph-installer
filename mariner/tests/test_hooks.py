import pytest
from mariner import hooks


class FakeState(object):

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


class TestAnsibleExists(object):

    def test_ansible_is_there(self, monkeypatch):
        monkeypatch.setattr(
            hooks, 'which',
            lambda x: '/usr/bin/ansible-playbook')
        assert hooks.ansible_exists() is None

    def test_ansible_is_not_there(self, monkeypatch):
        monkeypatch.setattr(
            hooks, 'which',
            lambda x: None)
        with pytest.raises(hooks.SystemCheckError):
            hooks.ansible_exists()


class TestCeleryHasWorkers(object):

    def test_celery_has_workers(self, monkeypatch):
        stats = lambda: {'value': 'some stat'}
        monkeypatch.setattr(
            hooks, 'inspect',
            lambda: FakeState(stats=stats))
        assert hooks.celery_has_workers() is None

    def test_celery_has_no_workers(self, monkeypatch):
        monkeypatch.setattr(
            hooks, 'inspect',
            lambda: FakeState(stats=lambda: None))
        with pytest.raises(hooks.SystemCheckError):
            hooks.celery_has_workers()


class TestRabbitMQIsRunning(object):

    def test_is_running(self, monkeypatch):
        def errors(): raise IOError
        monkeypatch.setattr(
            hooks, 'celery_has_workers',
            errors)
        with pytest.raises(hooks.SystemCheckError):
            assert hooks.rabbitmq_is_running()

    def test_is_not_running(self, monkeypatch):
        monkeypatch.setattr(
            hooks, 'celery_has_workers',
            lambda: None)
        assert hooks.rabbitmq_is_running() is None
