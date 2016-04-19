from sqlalchemy import Column, Integer, String,  Boolean, DateTime, UnicodeText
from sqlalchemy.orm.exc import DetachedInstanceError
from ceph_installer.models import Base


class Task(Base):

    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    identifier = Column(String(256), unique=True, nullable=False, index=True)
    endpoint = Column(String(256), index=True)
    command = Column(String(256))
    stderr = Column(UnicodeText)
    stdout = Column(UnicodeText)
    started = Column(DateTime)
    ended = Column(DateTime)
    succeeded = Column(Boolean(), default=False)
    exit_code = Column(Integer)

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
        )
