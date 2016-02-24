from ceph_installer import hooks
from ceph_installer.controllers import status


def generic_system_error():
    msg = "important system is not running"
    raise hooks.SystemCheckError(msg)

error_checks = (
    generic_system_error,
)

ok_checks = (
    lambda: True,
)


class TestSetupController(object):

    def test_index_system_error_message(self, session, monkeypatch):
        monkeypatch.setattr(status, 'system_checks', error_checks)
        result = session.app.get("/api/status/", expect_errors=True)
        assert result.json['message'] == 'important system is not running'

    def test_index_system_error_code(self, session, monkeypatch):
        monkeypatch.setattr(status, 'system_checks', error_checks)
        result = session.app.get("/api/status/", expect_errors=True)
        assert result.status_int == 500

    def test_index_system_ok_message(self, session, monkeypatch):
        monkeypatch.setattr(status, 'system_checks', ok_checks)
        result = session.app.get("/api/status/")
        assert result.json['message'] == "ok"

    def test_index_system_ok_status(self, session, monkeypatch):
        monkeypatch.setattr(status, 'system_checks', ok_checks)
        result = session.app.get("/api/status/")
        assert result.status_int == 200
