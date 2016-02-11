

class TestSchemaErrors(object):

    def test_install_empty_object(self, session):
        result = session.app.post_json("/api/mon/install/", params=dict(),
                                       expect_errors=True)
        message = result.json['message']
        assert message.endswith('an empty dictionary object was provided')

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
