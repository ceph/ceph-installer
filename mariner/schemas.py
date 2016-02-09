from notario.validators import types
from notario.decorators import optional


def list_of_hosts(value):
    assert isinstance(value, list), "requires format: ['host1', 'host2']"


install_schema = (
    (optional("adjust-repos"), types.boolean),
    (optional("gpg-url"), types.string),
    ("hosts", list_of_hosts),
    (optional("release"), types.string),
    (optional("repo-only"), types.boolean),
    (optional("repo-url"), types.string),
)
