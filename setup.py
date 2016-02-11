# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='ceph-installer',
    version='0.1',
    description='An HTTP API that provides Ceph installation/configuration endpoints',
    author='',
    author_email='',
    install_requires=[
        'pecan',
        'celery',
        'sqlalchemy',
        'gunicorn',
        'pecan-notario',
    ],
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(exclude=['ez_setup']),
    entry_points="""
        [pecan.command]
        populate=mariner_installer.commands.populate:PopulateCommand
        """
)
