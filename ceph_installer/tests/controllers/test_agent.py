from ceph_installer.controllers import agent


class TestAgentController(object):

    def test_index_get_is_not_allowed(self, session):
        result = session.app.get("/api/agent/", expect_errors=True)
        assert result.status_int == 405

    def test_index_incorrect_schema(self, session):
        data = dict(hosts=["google.com"], bogus="foo")
        result = session.app.post_json("/api/agent/", params=data,
                                       expect_errors=True)
        assert result.status_int == 400

    def test_index_post_works_with_right_schema(self, session, monkeypatch):
        monkeypatch.setattr(agent.call_ansible, 'apply_async', lambda args, kwargs: None)
        data = dict(hosts=["node1"])
        result = session.app.post_json("/api/agent/", params=data)
        assert result.json['endpoint'] == '/api/agent/'
        assert result.json['identifier'] is not None

    def test_invalid_master_value_is_detected(self, session, monkeypatch):
        data = dict(hosts=["google.com"], master=1)
        result = session.app.post_json("/api/agent/", params=data,
                                       expect_errors=True)
        assert result.status_int == 400
        assert result.json['message'].endswith('not of type string')

    def test_master_is_defined_and_used(self, session, monkeypatch, argtest):
        monkeypatch.setattr(agent.call_ansible, 'apply_async', argtest)
        data = dict(hosts=["node1"], master='installer.host')
        session.app.post_json("/api/agent/", params=data)
        # argtest.kwargs['kwargs'] may look a bit redundant, but celery tasks
        # require that same signature as the 'recorder' fixture we have to
        # capture args and kwargs
        ansible_extra_args = argtest.kwargs['kwargs']['extra_vars']
        assert ansible_extra_args['agent_master_host'] == 'installer.host'

    def test_master_is_not_defined_and_is_inferred(self, session, monkeypatch, argtest):
        monkeypatch.setattr(agent.call_ansible, 'apply_async', argtest)
        data = dict(hosts=["node1"])
        session.app.post_json("/api/agent/", params=data)
        ansible_extra_args = argtest.kwargs['kwargs']['extra_vars']
        assert ansible_extra_args['agent_master_host'] == 'localhost'


class TestAgentVerbose(object):

    def test_install_verbose(self, session, monkeypatch, argtest):
        monkeypatch.setattr(
            agent.call_ansible, 'apply_async', argtest)
        data = {"hosts": ["node1"], "verbose": True}
        session.app.post_json("/api/agent/", params=data)
        kwargs = argtest.kwargs['kwargs']
        assert kwargs['verbose'] is True

    def test_install_non_verbose(self, session, monkeypatch, argtest):
        monkeypatch.setattr(
            agent.call_ansible, 'apply_async', argtest)
        data = {"hosts": ["node1"]}
        session.app.post_json("/api/agent/", params=data)
        kwargs = argtest.kwargs['kwargs']
        assert kwargs['verbose'] is False
