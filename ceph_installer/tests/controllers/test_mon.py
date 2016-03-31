from ceph_installer.controllers import mon


class TestMonController(object):

    def setup(self):
        self.configure_data = dict(
            monitor_secret="secret",
            public_network="0.0.0.0/24",
            host="node1",
            interface="eth0",
            fsid="1720107309134",
        )

    def test_index_get(self, session):
        result = session.app.get("/api/mon/")
        assert result.status_int == 200

    def test_install_missing_hosts(self, session):
        result = session.app.post_json("/api/mon/install/", params=dict(),
                                       expect_errors=True)
        assert result.status_int == 400

    def test_install_bogus_field(self, session):
        data = dict(hosts=["google.com"], bogus="foo")
        result = session.app.post_json("/api/mon/install/", params=data,
                                       expect_errors=True)
        assert result.status_int == 400

    def test_install_hosts_not_a_list(self, session):
        data = dict(hosts="google.com")
        result = session.app.post_json("/api/mon/install/", params=data,
                                       expect_errors=True)
        assert result.status_int == 400

    def test_install_hosts(self, session, monkeypatch):
        monkeypatch.setattr(mon.call_ansible, 'apply_async', lambda args, kwargs: None)
        data = dict(hosts=["node1"])
        result = session.app.post_json("/api/mon/install/", params=data,
                                       expect_errors=True)
        assert result.json['endpoint'] == '/api/mon/install/'
        assert result.json['identifier'] is not None

    def test_configure_missing_fields(self, session):
        data = dict()
        result = session.app.post_json("/api/mon/configure/", params=data,
                                       expect_errors=True)
        assert result.status_int == 400

    def test_configure_hosts(self, session, monkeypatch):
        monkeypatch.setattr(mon.call_ansible, 'apply_async', lambda args, kwargs: None)
        result = session.app.post_json("/api/mon/configure/", params=self.configure_data)
        assert result.json['endpoint'] == '/api/mon/configure/'
        assert result.json['identifier'] is not None

    def test_configure_with_cluster_name(self, session, monkeypatch, argtest):
        monkeypatch.setattr(mon.call_ansible, 'apply_async', argtest)
        self.configure_data['cluster_name'] = "lol"
        session.app.post_json("/api/mon/configure/", params=self.configure_data)
        extra_vars = argtest.kwargs['kwargs']['extra_vars']
        assert "cluster" in extra_vars
        assert "cluster_name" not in extra_vars
        assert extra_vars["cluster"] == "lol"

    def test_configure_with_conf(self, session, monkeypatch):
        monkeypatch.setattr(mon.call_ansible, 'apply_async', lambda args, kwargs: None)
        self.configure_data['conf'] = {"global": {"auth supported": "cephx"}}
        result = session.app.post_json("/api/mon/configure/", params=self.configure_data)
        assert result.json['endpoint'] == '/api/mon/configure/'
        assert result.json['identifier'] is not None

    def test_configure_with_invalid_conf(self, session, monkeypatch):
        monkeypatch.setattr(mon.call_ansible, 'apply_async', lambda args, kwargs: None)
        self.configure_data['conf'] = {"global": {"auth supported": "cephx"}, "monn": 1}
        result = session.app.post_json("/api/mon/configure/", params=self.configure_data,
                                       expect_errors=True)
        assert result.status_int == 400
        assert "unexpected item in data" in result.json["message"]

    def test_configure_monitors_not_a_list(self, session, monkeypatch):
        monkeypatch.setattr(mon.call_ansible, 'apply_async', lambda args, kwargs: None)
        data = self.configure_data.copy()
        data["monitors"] = "invalid"
        result = session.app.post_json("/api/mon/configure/", params=data,
                                       expect_errors=True)
        assert result.status_int == 400
        assert "monitors" in result.json["message"]

    def test_configure_monitors_not_a_list_of_objects(self, session, monkeypatch):
        monkeypatch.setattr(mon.call_ansible, 'apply_async', lambda args, kwargs: None)
        data = self.configure_data.copy()
        data["monitors"] = "['mon1', 'mon2']"
        result = session.app.post_json("/api/mon/configure/", params=data,
                                       expect_errors=True)
        assert result.status_int == 400
        assert "monitors" in result.json["message"]

    def test_configure_monitors_missing_host_key(self, session, monkeypatch):
        monkeypatch.setattr(mon.call_ansible, 'apply_async', lambda args, kwargs: None)
        mons = [{"foo": "bar"}]
        data = self.configure_data.copy()
        data['monitors'] = mons
        result = session.app.post_json("/api/mon/configure/", params=data,
                                       expect_errors=True)
        assert result.status_int == 400
        assert "monitors" in result.json["message"]

    def test_configure_monitors_missing_interface_key(self, session, monkeypatch):
        monkeypatch.setattr(mon.call_ansible, 'apply_async', lambda args, kwargs: None)
        mons = [{"host": "mon0.host"}]
        data = self.configure_data.copy()
        data['monitors'] = mons
        result = session.app.post_json("/api/mon/configure/", params=data,
                                       expect_errors=True)
        assert result.status_int == 400
        assert "monitors" in result.json["message"]

    def test_configure_valid_monitors(self, session, monkeypatch):
        def check(args, kwargs):
            inventory = args[0]
            hosts = inventory[0][1]
            assert "node1 monitor_interface=eth0" in hosts
            assert "mon1.host monitor_interface=eth1" in hosts

        monkeypatch.setattr(mon.call_ansible, 'apply_async', check)
        mons = [{"host": "mon1.host", "interface": "eth1"}]
        data = self.configure_data.copy()
        data["monitors"] = mons
        result = session.app.post_json("/api/mon/configure/", params=data)
        assert result.json['endpoint'] == '/api/mon/configure/'
        assert result.json['identifier'] is not None


class TestMonWithCalamari(object):

    def setup(self):
        self.configure_data = dict(
            calamari=True,
            monitor_secret="secret",
            public_network="0.0.0.0/24",
            host="node1",
            interface="eth0",
            fsid="1720107309134",
        )

    def test_install_with_calamari(self, session, monkeypatch, argtest):
        monkeypatch.setattr(
            mon.call_ansible, 'apply_async', argtest)
        data = {"hosts": ["node1"], "calamari": True}
        session.app.post_json("/api/mon/install/", params=data)
        extra_vars = argtest.kwargs['kwargs']['extra_vars']
        assert extra_vars['calamari'] is True

    def test_install_without_calamari(self, session, monkeypatch, argtest):
        monkeypatch.setattr(
            mon.call_ansible, 'apply_async', argtest)
        data = {"hosts": ["node1"]}
        session.app.post_json("/api/mon/install/", params=data)
        extra_vars = argtest.kwargs['kwargs']['extra_vars']
        assert extra_vars['calamari'] is False

    def test_configure_with_calamari(self, session, monkeypatch, argtest):
        monkeypatch.setattr(
            mon.call_ansible, 'apply_async', argtest)
        session.app.post_json("/api/mon/configure/", params=self.configure_data)
        extra_vars = argtest.kwargs['kwargs']['extra_vars']
        assert extra_vars['calamari'] is True

    def test_configure_without_calamari(self, session, monkeypatch, argtest):
        monkeypatch.setattr(
            mon.call_ansible, 'apply_async', argtest)
        self.configure_data.pop('calamari')
        session.app.post_json("/api/mon/configure/", params=self.configure_data)
        extra_vars = argtest.kwargs['kwargs']['extra_vars']
        # 'calamari' will not be passed in as it wasn't defined explicitly
        assert extra_vars.get('calamari') is None


class TestMonVerbose(object):

    def setup(self):
        self.configure_data = dict(
            verbose=True,
            monitor_secret="secret",
            public_network="0.0.0.0/24",
            host="node1",
            interface="eth0",
            fsid="1720107309134",
        )
        self.configure_data_addr = dict(
            verbose=True,
            monitor_secret="secret",
            public_network="0.0.0.0/24",
            host="node1",
            address="10.0.0.1",
            fsid="1720107309134",
        )

    def test_install_verbose(self, session, monkeypatch, argtest):
        monkeypatch.setattr(
            mon.call_ansible, 'apply_async', argtest)
        data = {"hosts": ["node1"], "verbose": True}
        session.app.post_json("/api/mon/install/", params=data)
        kwargs = argtest.kwargs['kwargs']
        assert kwargs['verbose'] is True

    def test_install_non_verbose(self, session, monkeypatch, argtest):
        monkeypatch.setattr(
            mon.call_ansible, 'apply_async', argtest)
        data = {"hosts": ["node1"]}
        session.app.post_json("/api/mon/install/", params=data)
        kwargs = argtest.kwargs['kwargs']
        assert kwargs['verbose'] is False

    def test_configure_verbose(self, session, monkeypatch, argtest):
        monkeypatch.setattr(
            mon.call_ansible, 'apply_async', argtest)
        session.app.post_json("/api/mon/configure/", params=self.configure_data)
        kwargs = argtest.kwargs['kwargs']
        assert kwargs['verbose'] is True

    def test_configure_non_verbose(self, session, monkeypatch, argtest):
        monkeypatch.setattr(
            mon.call_ansible, 'apply_async', argtest)
        self.configure_data.pop('verbose')
        session.app.post_json("/api/mon/configure/", params=self.configure_data)
        kwargs = argtest.kwargs['kwargs']
        assert kwargs['verbose'] is False

    def test_configure_with_monitor_address(self, session, monkeypatch, argtest):
        monkeypatch.setattr(
            mon.call_ansible, 'apply_async', argtest)
        session.app.post_json("/api/mon/configure/", params=self.configure_data_addr)
        args = argtest.kwargs['args'][0][0]
        assert args == ('mons', [u'node1 monitor_address=10.0.0.1'])

    def test_configure_with_monitor_interface(self, session, monkeypatch, argtest):
        monkeypatch.setattr(
            mon.call_ansible, 'apply_async', argtest)
        session.app.post_json("/api/mon/configure/", params=self.configure_data)
        args = argtest.kwargs['args'][0][0]
        assert args == ('mons', [u'node1 monitor_interface=eth0'])
