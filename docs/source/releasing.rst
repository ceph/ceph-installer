.. releasing:

ceph-installer release process
==============================

When you are ready to cut a new version:

#. Modify ``docs/source/changelog.rst`` with the changes since the latest
   release. Optionally, the ``gitchangelog`` program can help you write this.

#. Bump the version number in ``ceph_installer/__init__.py`` and commit your
   changes.
   ::

      python setup.py bump

#. Tag and release to PyPI.
   ::

      python setup.py release
