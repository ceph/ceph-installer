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

``/cluster/{id}/``
------------------

``mon``
=======

``/cluster/{cluster-id}/mon/``
------------------------------

``/cluster/{cluster-id}/mon/{mon-id}/``
---------------------------------------

``/cluster/{cluster-id}/mon/{mon-id}/install/``
-----------------------------------------------

``/cluster/{cluster-id}/mon/{mon-id}/configure/``
-------------------------------------------------

``osd``
=======

``/cluster/{cluster-id}/osd/``
------------------------------

``/cluster/{cluster-id}/osd/{osd-id}/``
---------------------------------------

``/cluster/{cluster-id}/osd/{osd-id}/install/``
-----------------------------------------------

``/cluster/{cluster-id}/osd/{osd-id}/configure/``
-------------------------------------------------

``journal``
===========

``/cluster/{cluster-id}/journal/``
----------------------------------

``/cluster/{cluster-id}/journal/{journal-id}/``
-----------------------------------------------

``/cluster/{cluster-id}/journal/{journal-id}/install/``
-------------------------------------------------------

``/cluster/{cluster-id}/journal/{journal-id}/configure/``
---------------------------------------------------------


``rgw``
=======

``/cluster/{cluster-id}/rgw/``
------------------------------

``/cluster/{cluster-id}/rgw/{rgw-id}/``
---------------------------------------

``/cluster/{cluster-id}/rgw/{rgw-id}/install/``
-----------------------------------------------

``/cluster/{cluster-id}/rgw/{rgw-id}/configure/``
-------------------------------------------------

``calamari``
============

``/cluster/{cluster-id}/calamari/``
-----------------------------------

``/cluster/{cluster-id}/calamari/{calamari-id}/``
-------------------------------------------------

``/cluster/{cluster-id}/calamari/{calamari-id}/install/``
---------------------------------------------------------

``/cluster/{cluster-id}/calamari/{calamari-id}/configure/``
-----------------------------------------------------------

