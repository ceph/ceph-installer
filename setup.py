# -*- coding: utf-8 -*-
import subprocess
try:
    from setuptools import setup, find_packages, Command
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages, Command
import re


module_file = open("ceph_installer/__init__.py").read()
metadata = dict(re.findall("__([a-z]+)__\s*=\s*'([^']+)'", module_file))
long_description = open('README.rst').read()
version = metadata['version']


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
        print ' '.join(cmd)
        subprocess.check_call(cmd)

        # Push Git tag to origin remote
        cmd = ['git', 'push', 'origin', tag_name]
        print ' '.join(cmd)
        subprocess.check_call(cmd)

        # Push package to pypi
        cmd = ['python', 'setup.py', 'sdist', 'upload']
        if self.sign:
            cmd.append('--sign')
        print ' '.join(cmd)
        subprocess.check_call(cmd)


setup(
    name='ceph-installer',
    version=version,
    description='An HTTP API that provides Ceph installation/configuration endpoints',
    long_description=long_description,
    author='',
    author_email='',
    scripts=['bin/ceph-installer'],
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
    cmdclass={'release': ReleaseCommand},
)
