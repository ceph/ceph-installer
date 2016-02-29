from ceph_installer import models, tasks


class TestCallAnsible(object):

    def setup(self):
        models.Task(
            identifier='aaaa',
            endpoint='/api/test/',
        )
        models.commit()

    def test_set_exit_code_on_error(self, session):
        tasks.call_ansible.apply(args=([], 'aaaa')).get()
        task = models.Task.get(1)
        assert task.exit_code == -1

    def test_set_exception_on_stderr(self, session, monkeypatch):
        def error(*a, **kw): raise OSError('a severe error')
        monkeypatch.setattr(tasks.process, 'run', error)
        tasks.call_ansible.apply(args=([], 'aaaa')).get()
        task = models.Task.get(1)
        assert task.stderr == 'a severe error'
