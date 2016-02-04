import subprocess
import tempfile
import logging
from mariner.util import which, get_playbook_path

logger = logging.getLogger(__name__)


def make_ansible_command(hosts_file, identifier, extra_vars='{}', tags=''):
    """
    This utility will compose the command needed to run ansible, capture its
    stdout and stderr to a file
    """
    playbook = get_playbook_path()
    ansible_path = which('ansible-playbook')

    return [
        ansible_path, '-i', hosts_file,
        '--extra-vars="%s"' % extra_vars, '--tags', tags, playbook
    ]


def temp_file(identifier, std):
    return tempfile.NamedTemporaryFile(
        prefix="{identifier}_{std}".format(
            identifier=identifier, std=std), delete=False
    )


def run(arguments, **kwargs):
    """
    A small helper to run a system command using ``subprocess.Popen``. Opinionated becuase
    it will always want to
    Safely execute a ``subprocess.Popen`` call making sure that the
    executable exists and raising a helpful error message
    if it does not.

    .. note:: This should be the prefered way of calling ``subprocess.Popen``
    since it provides the caller with the safety net of making sure that
    executables *will* be found and will error nicely otherwise.

    This returns the output of the command and the return code of the
    process in a tuple: (output, returncode).
    """
    logger.info('Running command: %s' % ' '.join(arguments))
    process = subprocess.Popen(
        arguments,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **kwargs)
    out, err = process.communicate()
    return out, err, process.returncode
