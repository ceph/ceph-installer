from notario.validators import types
from notario.decorators import optional


def list_of_hosts(value):
    assert isinstance(value, list), "requires format: ['host1', 'host2']"


install_schema = (
    ("hosts", list_of_hosts),
    (optional("redhat_storage"), types.boolean),
)
