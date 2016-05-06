from sqlalchemy import Column, Integer, String,  Boolean, DateTime, UnicodeText
from sqlalchemy.orm.exc import DetachedInstanceError
from ceph_installer.models import Base


class Task(Base):

    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    identifier = Column(String(256), unique=True, nullable=False, index=True)
    endpoint = Column(String(256), index=True)
    user_agent = Column(String(512))
    request = Column(UnicodeText)
    http_method = Column(String(64))
    command = Column(String(256))
    stderr = Column(UnicodeText)
    stdout = Column(UnicodeText)
    started = Column(DateTime)
    ended = Column(DateTime)
    succeeded = Column(Boolean(), default=False)
    exit_code = Column(Integer)

    def __init__(self, request=None, **kw):
        self._extract_request_metadata(request)
        for k, v in kw.items():
            setattr(self, k, v)

    def _extract_request_metadata(self, request):
        self.http_method = getattr(request, 'method', '')
        self.request = str(getattr(request, 'body', ''))
        self.user_agent = getattr(request, 'user_agent', '')

    def __repr__(self):
        try:
            return '<Task %r>' % self.identifier
        except DetachedInstanceError:
            return '<Task detached>'

    def __json__(self):
        return dict(
            identifier = self.identifier,
            endpoint = self.endpoint,
            command = self.command,
            stderr = self.stderr,
            stdout = self.stdout,
            started = self.started,
            ended = self.ended,
            succeeded = self.succeeded,
            exit_code = self.exit_code,
            user_agent = self.user_agent,
            request = self.request,
            http_method = self.http_method,
        )
