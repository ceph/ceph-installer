"""
This is really not a logging facility. For the CLI we only require a nice color
output on some interactions. Full logging is not needed.
"""
import sys
from ceph_installer.cli import util


def error(message):
    line = "%s %s\n" % (util.red_arrow, message)
    line = line.encode("utf-8")
    sys.stderr.write(line)


def debug(message):
    line = "%s %s\n" % (util.blue_arrow, message)
    line = line.encode("utf-8")
    sys.stdout.write(line)


def info(message):
    line = "%s %s\n" % (util.bold_arrow, message)
    line = line.encode("utf-8")
    sys.stdout.write(line)


def warning(message):
    line = "%s %s\n" % (util.yellow_arrow, message)
    line = line.encode("utf-8")
    sys.stderr.write(line)
