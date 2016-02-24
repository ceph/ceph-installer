.. releasing:

ceph-installer release process
==============================

When you are ready to cut a new version:

#. Bump the version number in setup.py.
   ::

      vim setup.py

#. Commit your setup.py change as "version 1.2.3".
   ::

      git commit setup.py -m 'version 1.2.3'

#. Tag and release to PyPI (known as "py-p-i" for you plebs).
   ::

      python setup.py release

#. Push your setup.py change directly to master on GitHub.
   ::

      git push origin master

