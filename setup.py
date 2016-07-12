# -*- coding: utf-8 -*-
import subprocess
try:
    from setuptools import setup, find_packages, Command
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages, Command
import re


def read_module_contents():
    with open('ceph_installer/__init__.py') as installer_init:
        return installer_init.read()

module_file = read_module_contents()
metadata = dict(re.findall("__([a-z]+)__\s*=\s*'([^']+)'", module_file))
long_description = open('README.rst').read()
version = metadata['version']


class BumpCommand(Command):
    """ Bump the __version__ number and commit all changes. """

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        version = metadata['version'].split('.')
        version[-1] = str(int(version[-1]) + 1)  # Bump the final part

        try:
            print('old version: %s  new version: %s' %
                  (metadata['version'], '.'.join(version)))
            raw_input('Press enter to confirm, or ctrl-c to exit >')
        except KeyboardInterrupt:
            raise SystemExit("\nNot proceeding")

        old = "__version__ = '%s'" % metadata['version']
        new = "__version__ = '%s'" % '.'.join(version)

        module_file = read_module_contents()
        with open('ceph_installer/__init__.py', 'w') as fileh:
            fileh.write(module_file.replace(old, new))

        # Commit everything with a standard commit message
        cmd = ['git', 'commit', '-a', '-m', 'version %s' % '.'.join(version)]
        print(' '.join(cmd))
        subprocess.check_call(cmd)


class ReleaseCommand(Command):
    """ Tag and push a new release. """

    user_options = [('sign', 's', 'GPG-sign the Git tag and release files')]

    def initialize_options(self):
        self.sign = False

    def finalize_options(self):
        pass

    def run(self):
        # Create Git tag
        tag_name = 'v%s' % version
        cmd = ['git', 'tag', '-a', tag_name, '-m', 'version %s' % version]
        if self.sign:
            cmd.append('-s')
        print(' '.join(cmd))
        subprocess.check_call(cmd)

        # Push Git tag to origin remote
        cmd = ['git', 'push', 'origin', tag_name]
        print(' '.join(cmd))
        subprocess.check_call(cmd)

        # Push package to pypi
        cmd = ['python', 'setup.py', 'sdist', 'upload']
        if self.sign:
            cmd.append('--sign')
        print(' '.join(cmd))
        subprocess.check_call(cmd)

        # Push master to the remote
        cmd = ['git', 'push', 'origin', 'master']
        print(' '.join(cmd))
        subprocess.check_call(cmd)


setup(
    name='ceph-installer',
    version=version,
    description='An HTTP API that provides Ceph installation/configuration endpoints',
    long_description=long_description,
    author='',
    author_email='',
    scripts=['bin/ceph-installer', 'bin/ceph-installer-celery', 'bin/ceph-installer-gunicorn'],
    install_requires=[
        'celery',
        'gunicorn',
        'notario>=0.0.11',
        'pecan>=1',
        'pecan-notario',
        'requests',
        'sqlalchemy',
        'tambo',
    ],
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(exclude=['ez_setup']),
    entry_points="""
        [pecan.command]
        populate=ceph_installer.commands.populate:PopulateCommand
        """,
    cmdclass={'bump': BumpCommand, 'release': ReleaseCommand},
)
