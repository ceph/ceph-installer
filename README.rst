Mariner
=======
An HTTP API to provision and control the deployment process of Ceph clusters.


Restful HTTP API
----------------
The service allows to interact with different clusters via a RestFul API that
accepts and returns JSON responses along with meaningful error codes and
messages.

Most if not all requests should use canonicalized URLs (they end with
a trailing slash).

It follows these concepts:

* ``GET`` operations are read-only operations. They will not trigger any
  behavior.

* ``POST`` requests will create resources or trigger a specific behavior, like
  installing operations on a given host.

* ``PUT`` requests will be processed as updates to a given resources.

* ``DELETE`` will cause destruction of a resource.


Endpoints
=========
The parent endpoint for any cluster interaction is ``/cluster/``

``cluster``
===========

``/cluster/``
-------------
GET
POST

``/cluster/{id}/``
------------------
GET
DELETE
PUT

``mon``
=======

``/cluster/{cluster-id}/mon/``
------------------------------
GET
POST

``/cluster/{cluster-id}/mon/{mon-id}/``
---------------------------------------
GET
DELETE
PUT

``/cluster/{cluster-id}/mon/{mon-id}/install/``
-----------------------------------------------
GET
POST

``/cluster/{cluster-id}/mon/{mon-id}/configure/``
-------------------------------------------------
GET
POST

``osd``
=======

``/cluster/{cluster-id}/osd/``
------------------------------
GET
DELETE
PUT

``/cluster/{cluster-id}/osd/{osd-id}/``
---------------------------------------
GET
POST

``/cluster/{cluster-id}/osd/{osd-id}/install/``
-----------------------------------------------
GET
POST

``/cluster/{cluster-id}/osd/{osd-id}/configure/``
-------------------------------------------------
GET
POST

XXX This might not be a good idea to implement since journal operations are
usually a subset of OSD commands.
``journal``
===========

``/cluster/{cluster-id}/journal/``
----------------------------------
GET
DELETE
PUT

``/cluster/{cluster-id}/journal/{journal-id}/``
-----------------------------------------------
GET
POST

``/cluster/{cluster-id}/journal/{journal-id}/install/``
-------------------------------------------------------
GET
POST

``/cluster/{cluster-id}/journal/{journal-id}/configure/``
---------------------------------------------------------
GET
POST


``rgw``
=======

``/cluster/{cluster-id}/rgw/``
------------------------------
GET
DELETE
PUT

``/cluster/{cluster-id}/rgw/{rgw-id}/``
---------------------------------------
GET
POST

``/cluster/{cluster-id}/rgw/{rgw-id}/install/``
-----------------------------------------------
GET
POST

``/cluster/{cluster-id}/rgw/{rgw-id}/configure/``
-------------------------------------------------
GET
POST

``calamari``
============

``/cluster/{cluster-id}/calamari/``
-----------------------------------
GET
DELETE
PUT

``/cluster/{cluster-id}/calamari/{calamari-id}/``
-------------------------------------------------
GET
POST

``/cluster/{cluster-id}/calamari/{calamari-id}/install/``
---------------------------------------------------------
GET
POST

``/cluster/{cluster-id}/calamari/{calamari-id}/configure/``
-----------------------------------------------------------
GET
POST
