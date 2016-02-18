import os
import subprocess
import tempfile
import logging
import json

from ceph_installer.util import which, get_ceph_ansible_path

logger = logging.getLogger(__name__)


def make_ansible_command(hosts_file, identifier, extra_vars=None, tags='', skip_tags='', playbook='site.yml.sample'):
    """
    This utility will compose the command needed to run ansible, capture its
    stdout and stderr to a file
    """
    ceph_ansible_path = get_ceph_ansible_path()
    playbook = os.path.join(ceph_ansible_path, playbook)
    ansible_path = which('ansible-playbook')
    if not extra_vars:
        extra_vars = dict()

    extra_vars = json.dumps(extra_vars)

    cmd = [
        ansible_path, '-u', 'ceph-installer', playbook, '-i', hosts_file, "--extra-vars", extra_vars,
    ]

    if tags:
        cmd.extend(['--tags', tags])

    if skip_tags:
        cmd.extend(['--skip-tags', skip_tags])

    return cmd


def temp_file(identifier, std):
    return tempfile.NamedTemporaryFile(
        prefix="{identifier}_{std}".format(
            identifier=identifier, std=std), delete=False
    )


def run(arguments, send_input=None, **kwargs):
    """
    A small helper to run a system command using ``subprocess.Popen``.

    This returns the output of the command and the return code of the process
    in a tuple::

        (stdout, stderr, returncode)
    """
    logger.info('Running command: %s' % ' '.join(arguments))
    process = subprocess.Popen(
        arguments,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **kwargs)
    if send_input:
        out, err = process.communicate(send_input)
    else:
        out, err = process.communicate()
    return out, err, process.returncode
