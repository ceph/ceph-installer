from os import path
from textwrap import dedent
from tambo import Transport

from ceph_installer import process
from ceph_installer.cli import log

this_dir = path.abspath(path.dirname(__file__))
top_dir = path.dirname(path.dirname(this_dir))
playbook_path = path.join(top_dir, 'deploy/playbooks')


class Dev(object):

    help = "Development options"
    options = ['--user', '--branch']
    _help = dedent("""
    Deploying the ceph-installer HTTP service to a remote server with ansible.
    This command wraps ansible and certain flags to make it easier to deploy
    a development version.

    Usage::

        ceph-installer dev $HOST

    Note: Requires a remote user with passwordless sudo. User defaults to
    "vagrant".

    Options:

    --user        Define a user to connect to the remote server. Defaults  to 'vagrant'
    --branch      What branch to use for the deployment. Defaults to 'master'
    -vvvv         Enable high verbosity when running ansible
    """)

    def __init__(self, arguments):
        self.arguments = arguments

    def main(self):
        parser = Transport(self.arguments, options=self.options, check_help=True)
        parser.catch_help = self._help
        parser.parse_args()
        parser.catches_help()
        branch = parser.get('--branch', 'master')
        user = parser.get('--user', 'vagrant')
        high_verbosity = '-vvvv' if parser.has('-vvvv') else '-v'
        if not parser.unknown_commands:
            log.error("it is required to pass a host to deploy to, but none was provided")
            raise SystemExit(1)

        command = [
            "ansible-playbook",
            "-i", "%s," % parser.unknown_commands[-1],
            high_verbosity,
            "-u", user,
            "--extra-vars", 'branch=%s' % branch,
            "deploy.yml",
        ]
        log.debug("Running command: %s" % ' '.join(command))
        out, err, code = process.run(command, cwd=playbook_path)
        log.error(err)
        log.debug(out)
