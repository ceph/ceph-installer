import sys

from tambo import Transport
import ceph_installer
from ceph_installer.cli import log
from ceph_installer.cli import dev
from ceph_installer.cli.decorators import catches


class CephInstaller(object):
    _help = """
A command line utility to install and configure Ceph using an HTTP API as a REST service
to call Ansible.

Version: %s

Global Options:
-h, --help, help    Show this program's help menu
--log, --logging    Set the level of logging. Acceptable values:
                    debug, warning, error, critical


%s
    """

    mapper = {'dev': dev.Dev}

    def __init__(self, argv=None, parse=True):
        self.plugin_help = "No plugins found/loaded"
        if argv is None:
            argv = sys.argv
        if parse:
            self.main(argv)

    def help(self, subhelp):
        version = ceph_installer.__version__
        return self._help % (version, subhelp)

    @catches(KeyboardInterrupt, logger=log)
    def main(self, argv):
        parser = Transport(argv, mapper=self.mapper,
                           options=[], check_help=False,
                           check_version=False)
        parser.parse_args()
        parser.catch_help = self.help(parser.subhelp())
        parser.catch_version = ceph_installer.__version__
        parser.mapper = self.mapper
        if len(argv) <= 1:
            return parser.print_help()
        parser.dispatch()
        parser.catches_help()
        parser.catches_version()
