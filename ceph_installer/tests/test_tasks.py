# -*- coding: utf8 -*-
from ceph_installer import models, tasks


class TestCallAnsible(object):

    def setup(self):
        models.Task(
            identifier='aaaa',
            endpoint='/api/test/',
        )
        models.commit()

    def test_set_exit_code_on_error(self, session, monkeypatch):
        monkeypatch.setattr(
            tasks.process,
            'make_ansible_command',
            lambda *a, **kw: ['echo']
        )
        tasks.call_ansible.apply(args=([], 'aaaa')).get()
        task = models.Task.get(1)
        assert task.exit_code == -1

    def test_set_exception_on_stderr(self, session, monkeypatch):
        def error(*a, **kw): raise OSError('a severe error')
        monkeypatch.setattr(tasks.process, 'run', error)
        monkeypatch.setattr(
            tasks.process,
            'make_ansible_command',
            lambda *a, **kw: ['echo']
        )
        tasks.call_ansible.apply(args=([], 'aaaa')).get()
        task = models.Task.get(1)
        assert task.stderr == 'a severe error'

    def test_handle_unicode_on_stderr(self, session, monkeypatch):
        monkeypatch.setattr(
            tasks.process, 'run',
            lambda *a, **kw: ['stdout', 'ᓆ'.decode('utf-8', 'replace'), 1])
        monkeypatch.setattr(
            tasks.process,
            'make_ansible_command',
            lambda *a, **kw: ['echo']
        )
        tasks.call_ansible.apply(args=([], 'aaaa')).get()
        task = models.Task.get(1)
        assert task.stderr == u'\u14c6'

    def test_handle_unicode_on_stdout(self, session, monkeypatch):
        monkeypatch.setattr(
            tasks.process, 'run',
            lambda *a, **kw: ['£'.decode('utf-8', 'replace'), 'stderr', 1])
        monkeypatch.setattr(
            tasks.process,
            'make_ansible_command',
            lambda *a, **kw: ['echo']
        )
        tasks.call_ansible.apply(args=([], 'aaaa')).get()
        task = models.Task.get(1)
        assert task.stdout == u'\xa3'

    def test_process_a_request_that_is_none(self, session, monkeypatch):
        monkeypatch.setattr(
            tasks.process,
            'make_ansible_command',
            lambda *a, **kw: ['echo']
        )
        tasks.call_ansible.apply(args=([], 'aaaa')).get()
        task = models.Task.get(1)
        assert task.http_method == ''
        assert task.user_agent == ''
        assert task.request == ''
