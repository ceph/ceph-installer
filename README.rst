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
The parent endpoint for any API interaction is ``/api/``

``api``
=======

``/api/``
---------
GET

``tasks``
=========

A task is created when any of the following endpoints are used and
can be used to track the progress of the operation, like installing or
configuring a monitor.

``/api/tasks/``
---------------
GET

``/api/tasks/{ task-id }/``
---------------------------
GET

``mon``
=======

``/api/mon/install/``
---------------------
POST

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
