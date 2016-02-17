import sys
import logging

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

    @catches(KeyboardInterrupt)
    def main(self, argv):
        # Set console logging first with some defaults, to prevent having exceptions
        # before hitting logging configuration. The defaults can/will get overridden
        # later.

        # Console Logger
        sh = logging.StreamHandler()
        sh.setFormatter(log.color_format())
        sh.setLevel(logging.WARNING)

        # because we're in a module already, __name__ is not the ancestor of
        # the rest of the package; use the root as the logger for everyone
        root_logger = logging.getLogger()

        # allow all levels at root_logger, handlers control individual levels
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(sh)

        options = [['--log', '--logging']]
        parser = Transport(argv, mapper=self.mapper,
                           options=options, check_help=False,
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
