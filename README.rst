Ceph Installer
==============
An HTTP API (previously known as the "mariner installer") to provision and
control the deployment process of Ceph clusters.


Restful HTTP API
----------------
The service allows you to install and configure ceph via a RestFul API that
accepts and returns JSON responses along with meaningful error codes and
messages.

Most if not all requests should use canonicalized URLs (they end with
a trailing slash).

It follows these concepts:

* ``GET`` operations are read-only operations. They will not trigger any
  behavior.

* ``POST`` requests will create resources or trigger a specific behavior, like
  installing operations on a given host.

Requirements and dependencies
-----------------------------
This service is intended to be installed by a system package manager (like yum
or apt) and ideally all requirements and dependencies should be taken care of.
This is the list of the current services and system dependencies needed:

System requirements:

* RabbitMQ
* Ansible

Application requirements:

* pecan
* celery
* sqlalchemy
* gunicorn
* notario
* pecan-notario


Ceph Versions
=============

The default for the ``/api/*/install`` endpoints is to install the latest upstream
stable version of ceph. If you'd like to install the latest Red Hat Ceph Storage ensure
that the node being provisioned is correctly entitled and that the ``redhat_storage`` option
is set to ``True`` in the json body you send to the install endpoint.


Endpoints
=========
The parent endpoint for any API interaction is ``/api/``. The service provides
a setup script as well that can be used to ensure a remote node can comply with
certain requirements like: a deployment user, ssh keys, and sudo permissions.

``setup``
=========

``/setup/``
-----------
* ``GET``: Generates a BASH script to be downloaded as ``setup.sh``. This
  script should be executed with super user privileges on the remote node as it
  will perform the following actions:

  * create an ``ceph-installer`` user
  * ensure that the ``ceph-installer`` user can use sudo without a password prompt
  * remove the ``requiretty`` from ``/etc/sudoers`` if set, so that SSH
    connections allow non-interactive sessions from using ``sudo``
  * retrieve the SSH key that will be used for provisioning (see
    :ref:`provisioning_key`)
  * append the provisioning key onto ``$HOME/ceph-installer/.ssh/authorized_keys``

.. _provisioning_key:

``/setup/key/``
---------------
This endpoint will serve the public SSH key *from the user that is running the
service* assuming the location of: ``$HOME/.ssh/id_rsa.pub``. If this file does
not exist the service will proceed to create one *while processing the
request*.


``api``
=======

``/api/``
---------
* ``GET``: Will return the current status of the service.

Responses:
^^^^^^^^^^
200: All components of the system are operational
Body: ``{}``

500: System Error
Body: ``{"message": "Sample Error message"}``

``tasks``
=========

A task is created when any of the following endpoints are used and
can be used to track the progress of the operation, like installing or
configuring a monitor.

``/api/tasks/``
---------------
* ``GET``: Returns a list of all available tasks.
Responses:
^^^^^^^^^^
200: Available tasks
Body ::

    [
        {'command': 'command arguments flags sample',
          'ended': '2016-01-27T15:03:23.438172',
          'endpoint': '/api/rgw/configure',
          'id': '2207bde6-4346-4a83-984a-40a5c00056c1',
          'started': '2016-01-27T15:03:22.638173',
          'stderr': 'command stderr',
          'stdout': 'command stdout',
          'succeeded': True,
        }
    ]


500: System Error
Body: ``{"message": "Sample Error message"}``

``/api/tasks/{ task-id }/``
---------------------------
* ``GET``: Distinct task metadata
Responses:
^^^^^^^^^^
200: All components of the system are operational
Body ::

    {'command': 'command arguments flags sample',
      'ended': '2016-01-27T15:03:23.438172',
      'endpoint': '/api/rgw/configure',
      'id': '2207bde6-4346-4a83-984a-40a5c00056c1',
      'started': '2016-01-27T15:03:22.638173',
      'stderr': 'command stderr',
      'stdout': 'command stdout'
    }


404: Task is not available
Body: ``{"message": "2207bde6-4346-4a83-984a-40a5c00056c1 is not available"}``

500: System Error
Body: ``{"message": "Sample Error message"}``

``mon``
=======

``/api/mon/install/``
---------------------
* ``POST``: Start the installation process for monitor(s)
Body ::

    {
        'hosts': ['mon1.example.com', 'mon2.example.com', 'mon3.example.com'],
        'redhat_storage': False
    }


``/api/mon/configure/``
-----------------------
* ``POST``: Configure monitor(s)
Body ::

    [
        {'address': '192.168.1.1', 'hostname': 'mon1.example.com'},
        {'address': '192.168.1.2', 'hostname': 'mon2.example.com'}
    ]


``osd``
=======


``/api/osd/install/``
---------------------
* ``POST``: Start the installation process for monitor(s)
Body ::

    {
        'hosts': ['osd1.example.com', 'osd2.example.com'],
        'redhat_storage': False
    }


``/api/osd/configure/``
-----------------------
* ``POST``: Configure OSD(s)
Body ::

    [
        {
            'devices': ['/dev/sdb'],
            'hostname': 'osd1.example.com',
            'journal_collocate': True
        },
        {
            'devices': ['/dev/sdc', '/dev/sdb'],
            'hostname': 'osd2.example.com',
            'journal': '/dev/sdd'
        }
    ]


``journal_collocate`` will use the same device as the OSD for the journal. This
is not ideal and might incur in a performance penalty.


``rgw``
=======


``/api/rgw/install/``
---------------------
* ``POST``: Start the installation process for monitor(s)
Body ::

    {
        'hosts': ['rgw1.example.com', 'rgw2.example.com'],
        'redhat_storage': False
    }


``/api/rgw/configure/``
-----------------------
* ``POST``: Configure OSD(s)
``name`` is optional, will default to ``rgw.$short-hostname``, using the
examples below, that would be ``rgw.node1`` and ``rgw.node2``. It is allowed to
specify a ``name`` to alter this default behavior.

Body ::

    [
        {
            'name': 'main',
            'hostname': 'rgw1.example.com',
        },
        {
            'hostname': 'rgw2.example.com',
        }
    ]


``calamari``
============

``/api/calamari/install/``
--------------------------
* ``POST``: Start the installation process for calamari
Body ::

    {
        'host': ['calamari.example.com'],
        'redhat_storage': False
    }

``/api/calamari/configure/``
----------------------------
# TODO
