import os
import tempfile
from pecan.testing import load_test_app

from copy import deepcopy
from pecan import conf
from pecan import configuration
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from ceph_installer import models as _db
import pytest

os.environ['HOME'] = tempfile.mkdtemp(suffix='.ceph-installer-home')

DBNAME = 'ceph_installertest.db'
BIND = 'sqlite:///' + os.environ['HOME']


def config_file():
    here = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(here, 'config.py')


@pytest.fixture
def fake():
    class Fake(object):
        def __init__(self, *a, **kw):
            for k, v, in kw.items():
                setattr(self, k, v)
    return Fake


@pytest.fixture
def argtest():
    """
    Simple helper to use with monkeypatch so that a callable can be inspected
    afterwards to see if it was called with certain arguments.
    """
    class TestArgs(object):
        def __call__(self, *args, **kwargs):
            self.args = list(args)
            self.kwargs = kwargs
    return TestArgs()


@pytest.fixture(scope='session')
def app(request):
    config = configuration.conf_from_file(config_file()).to_dict()

    # Add the appropriate connection string to the app config.
    config['sqlalchemy'] = {
        'url': '%s/%s' % (BIND, DBNAME),
        'echo':          True,
        'echo_pool':     True,
        'pool_recycle':  3600,
        'encoding':      'utf-8'
    }

    # Set up a fake app
    app = TestApp(load_test_app(config))
    return app


@pytest.fixture(scope='session')
def connection(app, request):
    """Session-wide test database."""
    # Connect and create the temporary database
    print "=" * 80
    print "CREATING TEMPORARY DATABASE FOR TESTS"
    print "=" * 80

    # Bind and create the database tables
    _db.clear()
    engine_url = '%s/%s' % (BIND, DBNAME)

    db_engine = create_engine(
        engine_url,
        encoding='utf-8',
        poolclass=NullPool)

    # AKA models.start()
    _db.Session.bind = db_engine
    _db.metadata.bind = _db.Session.bind

    _db.Base.metadata.create_all(db_engine)
    _db.commit()
    _db.clear()

    #connection = db_engine.connect()

    def teardown():
        _db.Base.metadata.drop_all(db_engine)

    request.addfinalizer(teardown)

    # Slap our test app on it
    _db.app = app
    return _db


@pytest.fixture(scope='function')
def session(connection, request):
    """Creates a new database session for a test."""
    _config = configuration.conf_from_file(config_file()).to_dict()
    config = deepcopy(_config)

    # Add the appropriate connection string to the app config.
    config['sqlalchemy'] = {
        'url': '%s/%s' % (BIND, DBNAME),
        'encoding': 'utf-8',
        'poolclass': NullPool
    }

    connection.start()

    def teardown():
        from sqlalchemy.engine import reflection

        # Tear down and dispose the DB binding
        connection.clear()

        # start a transaction
        engine = conf.sqlalchemy.engine
        conn = engine.connect()
        trans = conn.begin()

        inspector = reflection.Inspector.from_engine(engine)

        # gather all data first before dropping anything.
        # some DBs lock after things have been dropped in
        # a transaction.
        conn.execute("DELETE FROM  %s;" % (
            ', '.join(inspector.get_table_names())
        ))

        trans.commit()
        conn.close()

    request.addfinalizer(teardown)
    return connection


class TestApp(object):
    """
    A controller test starts a database transaction and creates a fake
    WSGI app.
    """

    __headers__ = {}

    def __init__(self, app):
        self.app = app

    def _do_request(self, url, method='GET', **kwargs):
        methods = {
            'GET': self.app.get,
            'POST': self.app.post,
            'POSTJ': self.app.post_json,
            'PUT': self.app.put,
            'DELETE': self.app.delete
        }
        kwargs.setdefault('headers', {}).update(self.__headers__)
        return methods.get(method, self.app.get)(str(url), **kwargs)

    def post_json(self, url, **kwargs):
        """
        @param (string) url - The URL to emulate a POST request to
        @returns (paste.fixture.TestResponse)
        """
        return self._do_request(url, 'POSTJ', **kwargs)

    def post(self, url, **kwargs):
        """
        @param (string) url - The URL to emulate a POST request to
        @returns (paste.fixture.TestResponse)
        """
        return self._do_request(url, 'POST', **kwargs)

    def get(self, url, **kwargs):
        """
        @param (string) url - The URL to emulate a GET request to
        @returns (paste.fixture.TestResponse)
        """
        return self._do_request(url, 'GET', **kwargs)

    def put(self, url, **kwargs):
        """
        @param (string) url - The URL to emulate a PUT request to
        @returns (paste.fixture.TestResponse)
        """
        return self._do_request(url, 'PUT', **kwargs)

    def delete(self, url, **kwargs):
        """
        @param (string) url - The URL to emulate a DELETE request to
        @returns (paste.fixture.TestResponse)
        """
        return self._do_request(url, 'DELETE', **kwargs)


# this console logging configuration is basically just to be able to see output
# in tests, and this file gets executed by py.test when it runs, so we get that
# for free.
import logging
# Console Logger
sh = logging.StreamHandler()
sh.setLevel(logging.WARNING)

formatter = logging.Formatter(
    fmt='%(asctime)s.%(msecs)03d %(process)d:%(levelname)s:%(name)s:%(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S',
)
sh.setFormatter(formatter)


# because we're in a module already, __name__ is not the ancestor of
# the rest of the package; use the root as the logger for everyone
root_logger = logging.getLogger()

# allow all levels at root_logger, handlers control individual levels
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(sh)

console_loglevel = logging.DEBUG  # start at DEBUG for now

# Console Logger
sh.setLevel(console_loglevel)
