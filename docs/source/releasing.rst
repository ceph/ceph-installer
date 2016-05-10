.. releasing:

ceph-installer release process
==============================

When you are ready to cut a new version:

#. Modify ``docs/source/changelog.rst`` with the changes since the latest
   release. Optionally, the ``gitchangelog`` program can help you write this.

#. Bump the version number in ceph_installer/__init__.py.
   ::

      vim ceph_installer/__init__.py

#. Commit your setup.py change as "version 1.2.3".
   ::

      git commit ceph_installer/__init__.py -m 'version 1.2.3'

#. Tag and release to PyPI.
   ::

      python setup.py release
