from notario.validators import types
from notario.decorators import optional

mon_install_schema = (
    (optional("adjust-repos"), types.boolean),
    (optional("gpg-url"), types.string),
    ("hosts", types.array),
    (optional("release"), types.string),
    (optional("repo-only"), types.boolean),
    (optional("repo-url"), types.string),
)
