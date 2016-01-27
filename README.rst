Mariner
=======
An HTTP API to provision and control the deployment process of Ceph clusters.


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


Endpoints
=========
The parent endpoint for any API interaction is ``/api/``.

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
Body: ``{"msg": "Sample Error message"}``

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
          'stdout': 'command stdout'
        }
    ]


500: System Error
Body: ``{"msg": "Sample Error message"}``

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
Body: ``{"msg": "2207bde6-4346-4a83-984a-40a5c00056c1 is not available"}``

500: System Error
Body: ``{"msg": "Sample Error message"}``

``mon``
=======

``/api/mon/install/``
---------------------
POST
Body: ``{}``

``/api/mon/configure/``
-----------------------
POST

``osd``
=======


``/api/osd/install/``
---------------------
POST

``/api/osd/configure/``
-----------------------
POST

XXX This might not be a good idea to implement since journal operations are
usually a subset of OSD commands.
``journal``
===========


``/api/journal/install/``
-------------------------
POST

``/api/journal/configure/``
---------------------------
POST


``rgw``
=======


``/api/rgw/install/``
---------------------
POST

``/api/rgw/configure/``
-----------------------
POST

``calamari``
============

``/api/calamari/install/``
--------------------------
POST

``/api/calamari/configure/``
----------------------------
POST
