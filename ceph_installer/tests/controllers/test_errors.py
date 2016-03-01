

class TestSchemaErrors(object):

    def test_install_empty_object(self, session):
        result = session.app.post_json("/api/mon/install/", params=dict(),
                                       expect_errors=True)
        message = result.json['message']
        assert message.endswith('an empty dictionary object was provided')

    def test_install_invalid_json(self, session):
        # note how we are not using post_json for the request
        result = session.app.post("/api/mon/install/", params={2: 1}, expect_errors=True)
        message = result.json['message']
        assert message == 'invalid JSON was received'

    def test_host_is_invalid(self, session):
        params = {'hosts': ''}
        result = session.app.post_json("/api/mon/install/", params=params,
                                       expect_errors=True)
        message = result.json['message']
        assert "hosts" in message
        assert message.endswith(
            "failed validation, requires format: ['host1', 'host2']"
        )

    def test_redhat_storage_is_wrong_type(self, session):
        params = {'hosts': ['node1'], 'redhat_storage': "foo"}
        result = session.app.post_json("/api/mon/install/", params=params,
                                       expect_errors=True)
        message = result.json['message']
        assert message.endswith('not of type boolean')
        assert 'redhat_storage' in message


class TestErrors(object):

    def test_unavailable(self, session):
        result = session.app.get("/errors/unavailable/",
                                 expect_errors=True)
        message = result.json['message']
        assert message == 'service unavailable'

    def test_forbidden(self, session):
        result = session.app.get("/errors/forbidden/",
                                 expect_errors=True)
        message = result.json['message']
        assert message == 'forbidden'

    def test_invalid(self, session):
        result = session.app.get("/errors/forbidden/",
                                 expect_errors=True)
        message = result.json['message']
        assert message == 'forbidden'
