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

Configure operations
--------------------
The configuration step for any node type (rgw, mon, osd, etc...) is *required*
to be per node. It is up to the caller to handle domain logic.

The ceph-installer API does not implement *any* logic to determine the path to
cluster creation. It instead provides a granular set of endpoints to allow the
caller for the flexibility it needs.

Install operations
------------------
The install requests to the API *are allowed to pass a list of multiple hosts*.

This process is not sequential: all hosts are operated against at
once and if a single host fails to install the entire task will report as
a failure. This is expected Ansible behavior and this API adheres to that.

Callers should expect failures to halt as soon as a failure (or error) is met.

Requirements and dependencies
-----------------------------
This service is intended to be installed by a system package manager (like yum
or apt) and ideally all requirements and dependencies should be taken care of.
This is the list of the current services and system dependencies needed:

System requirements:

* Ansible
* RabbitMQ

Application requirements:

* celery
* notario
* gunicorn
* pecan
* pecan-notario
* sqlalchemy

Ceph Versions
=============

The default for the ``/api/*/install`` endpoints is to install the latest
upstream stable version of ceph. If you'd like to install the latest Red Hat
Ceph Storage ensure that the node being provisioned is correctly entitled and
that the ``redhat_storage`` option is set to ``True`` in the JSON body you send
to the install endpoint.


Endpoints
=========
The parent endpoint for any API interaction is ``/api/``. The service provides
a setup script as well that can be used to ensure a remote node can comply with
certain requirements like: a deployment user, ssh keys, and sudo permissions.

The top level endpoints are:

* :ref:`setup`
* :ref:`api`


.. _setup:

``setup``
=========

.. http:get:: /setup/

  Generates a BASH script to be downloaded as ``setup.sh``. This
  script should be executed with super user privileges on the remote node as it
  will perform the following actions:

  * Ensure that Python 2 is present on the system
  * create an ``ceph-installer`` user
  * ensure that the ``ceph-installer`` user can use sudo without a password
    prompt
  * remove the ``requiretty`` from ``/etc/sudoers.d/ceph-installer``, so that
    SSH connections allow non-interactive sessions from using ``sudo``
  * retrieve the SSH key that will be used for provisioning (see
    :http:get:`/setup/key/`)
  * append the provisioning key onto
    ``$HOME/ceph-installer/.ssh/authorized_keys``

   **Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Disposition: attachment; filename=setup.sh
      Content-Type: application/octet-stream; charset=UTF-8

   :statuscode 200: no error
   :statuscode 500: Server Error (see :ref:`server_errors`)


.. http:get:: /setup/agent/

  Generates a BASH script to be downloaded as ``agent-setup.sh``. Just like the
  :http:get:`/setup/` endpoint but also installing and configuring the
  ``rhscon-agent`` in the system. This script should also be executed with
  super user privileges on the remote node and it will perform the same actions
  as :http:get:`/setup/` with the addition of the following:

  * install the ``rhscon-agent`` and configure the ``salt-minion`` to point
    back to the master server (uses the same host as where the
    ``ceph-installer`` service is running)


   **Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Disposition: attachment; filename=agent-setup.sh
      Content-Type: application/octet-stream; charset=UTF-8

   :statuscode 200: no error
   :statuscode 500: Server Error (see :ref:`server_errors`)


.. _provisioning_key:

.. http:get:: /setup/key/

  This endpoint will serve the public SSH key *from the user that is running
  the service* assuming the location of: ``$HOME/.ssh/id_rsa.pub``. If this
  file does not exist the service will proceed to create one *while processing
  the request*.

   **Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Disposition: attachment; filename=id_rsa.pub
      Content-Type: application/octet-stream; charset=UTF-8

   :statuscode 200: no error
   :statuscode 500: Server Error (see :ref:`server_errors`)


.. _api:

``api``
=======

.. http:get:: /api/

    Will return the current status of the service.

  **Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {}


   :statuscode 200: All components of the system are operational
   :statuscode 500: Server Error (see :ref:`server_errors`)


``tasks``
---------

A task is created when an action on a remote node is triggered (for example to
install packages on a monitor node).  They can be used to track the progress of
the operation, like installing or configuring a remote node.

Tasks contain metadata for these calls. This metadata includes items like:
start time, end time, success, stderr, stdout

You may consume the status of a task by polling the ``/api/tasks/`` endpoint.

Polling
-------
As soon as a call is performed and conditions are met for provisioning on
a remote node a "task" is created. This means the information is not atomic, it
is available as soon as the call proceeds to a remote node interaction and
information gets updated as the task completes.

When a task is not done it will have a ``null`` value for the ``ended`` key,
will default to ``"succeeded": "false"`` and it will have a ``completed`` key
that will be ``true`` when the task has finished.  These tasks have an unique
identifier.  The endpoints *will always return a 200 when they are available*.

Polling is not subject to handle state with HTTP status codes (e.g. 304)


.. http:get:: /api/tasks/

  Returns a list of all available tasks.

   **Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
          {"command": "command arguments flags sample",
            "ended": "2016-01-27T15:03:23.438172",
            "endpoint": "/api/rgw/configure",
            "id": "2207bde6-4346-4a83-984a-40a5c00056c1",
            "started": "2016-01-27T15:03:22.638173",
            "stderr": "command stderr",
            "stdout": "command stdout",
            "succeeded": true,
          }
      ]

   :statuscode 200: Available tasks
   :statuscode 500: Server Error (see :ref:`server_errors`)


.. http:get:: /api/tasks/(id)/

  Distinct task metadata

  **Response**:

  .. sourcecode:: http

     HTTP/1.1 200 OK
     Content-Type: application/json

     {
       "command": "command arguments flags sample",
       "ended": "2016-01-27T15:03:23.438172",
       "endpoint": "/api/rgw/configure",
       "id": "2207bde6-4346-4a83-984a-40a5c00056c1",
       "started": "2016-01-27T15:03:22.638173",
       "stderr": "command stderr",
       "stdout": "command stdout"
     }

  :statuscode 200: Task metadata exists
  :statuscode 404: Task does not exist
  :statuscode 500: Server Error (see :ref:`server_errors`)


``agent``
=========

.. http:post:: /api/agent/

   Start the installation process for ceph-agent(s)

   **Response**:

   .. sourcecode:: http

     HTTP/1.1 200 OK
     Content-Type: application/json

     {
         "endpoint": "/api/agent/",
         "succeeded": false,
         "stdout": null,
         "started": null,
         "exit_code": null,
         "ended": null,
         "command": null,
         "stderr": null,
         "identifier": "47f60562-a96b-4ac6-be07-71726b595793",
         "verbose": false,
     }

   **Request**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json


      {
          "hosts": ["mon1.example.com", "mon2.example.com", "mon3.example.com"],
          "master": "master.example.com"
      }

   :<json array hosts: (required) The hostnames to which to install and
                       configure. For simplicity's sake, the agent host's
                       salt-minion will point at a salt master on the same host
                       where ceph-installer is running.
   :<json string master: (optional, default: ``SERVER_NAME``) If not provided, it will look at the
                         request and use ``SERVER_NAME``.
   :<json boolean verbose: (optional, default: ``false``) Increase the verbosity when calling ansible.


``mon``
=======

.. http:post:: /api/mon/install/

   Start the installation process for monitor(s). It is allowed to flag the
   need to install the ``calamari-server`` package which provides a restful API
   for a cluster.

   **Response**:

   .. sourcecode:: http

     HTTP/1.1 200 OK
     Content-Type: application/json

     {
         "endpoint": "/api/mon/install/",
         "succeeded": false,
         "stdout": null,
         "started": null,
         "exit_code": null,
         "ended": null,
         "command": null,
         "stderr": null,
         "identifier": "47f60562-a96b-4ac6-be07-71726b595793"
     }

   **Request**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json


      {
          "calamari": false,
          "hosts": ["mon1.example.com", "mon2.example.com", "mon3.example.com"],
          "redhat_storage": false,
          "redhat_use_cdn": true,
          "verbose": false,
      }

   :<json boolean calamari: (optional, default: ``false``) include installation
                            of the ``calamari-server`` (a.k.a.
                            ``calamari-lite``)
   :<json array hosts: (required) The hostname to configure
   :<json boolean redhat_storage: (optional, default: ``false``) Use the
                                  downstream version of Red Hat Ceph Storage.
   :<json boolean redhat_use_cdn: (optional, default: ``true``) Use the Red Hat
                                  CDN and subscription-manager to install Red
                                  Hat Ceph Storage. This assumes the node is
                                  already registered with subscription-manager.
                                  If ``false``, Red Hat Ceph Storage will be
                                  installed by using repos that must have
                                  already been created on the node.
   :<json boolean verbose: (optional, default: ``false``) Increase the
                           verbosity when calling ansible.


.. http:post:: /api/mon/configure/

   Configure monitor(s)

   **Request**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "calamari": false,
          "conf": {"global": {"auth supported": "cephx"}},
          "host": "mon1.example.com",
          "interface": "eth0",
          "fsid": "deedcb4c-a67a-4997-93a6-92149ad2622a",
          "monitor_secret": "AQA7P8dWAAAAABAAH/tbiZQn/40Z8pr959UmEA==",
          "cluster_name": "my-ceph-cluster",
          "cluster_network": "192.0.2.0/24",
          "public_network": "198.51.100.0/24",
          "monitors": [{"host": "mon0.host", "interface": "eth1"}],
          "redhat_storage": false,
          "verbose": false,
      }


   :<json boolean calamari: (optional) include configuration of the
                            ``calamari-server`` (a.k.a.  ``calamari-lite``).
                            Defaults to ``false``.
   :<json object conf: (optional) An object that maps ceph.conf sections (only
                       global, mon, osd, rgw, mds allowed) to keys and values.
                       Anything defined in this mapping will override existing
                       settings.
   :<json string fsid: (required) The ``fsid`` for the cluster
   :<json string host: (required) The hostname to configure
   :<json string interface: (required if: ``address`` is not defined) The
                            interface name for the IP used by the monitor.
                            (e.g. "eth0") Either ``interface`` or ``address``
                            must be provided.
   :<json string address: (required if: ``interface`` is not defined) The IP
                          address of the monitor.  Either ``interface`` or
                          ``address`` must be provided.
   :<json string monitor_secret: (required) A key to use when creating the
                                 monitor keyrings.
   :<json string public_network: (required) The public network subnet for the
                                 cluster (in `CIDR`_ notation).
   :<json string cluster_network: (optional) If not provided, this will default
                                  to the ``public_network`` subnet (in `CIDR`_
                                  notation).
   :<json array monitors: (optional) This is only optional when no other
                          monitors currently exist
                          in the cluster. If you're configuring a mon for an
                          existing cluster, provide a list of objects
                          representing the monitor host and its ``interface``
                          or ``address``.
   :<json boolean redhat_storage: (optional) Use the downstream version of
                                  Red Hat Ceph Storage.
   :<json boolean verbose: (optional, default: ``false``) Increase the
                           verbosity when calling ansible.
   :<json string cluster_name: (optional, default: ``ceph``) Provide a custom
                               name for the ceph cluster.


``osd``
=======

.. http:post:: /api/osd/install/

   Start the installation process for OSD(s)

   **Response**:

   .. sourcecode:: http

     HTTP/1.1 200 OK
     Content-Type: application/json

     {
         "endpoint": "/api/osd/install/",
         "succeeded": false,
         "stdout": null,
         "started": null,
         "exit_code": null,
         "ended": null,
         "command": null,
         "stderr": null,
         "identifier": "47f60562-a96b-4ac6-be07-71726b595793"
     }

   **Request**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "hosts": ["osd1.example.com", "osd2.example.com"],
          "redhat_storage": false,
          "redhat_use_cdn": true,
          "verbose": false,
      }

   :<json array hosts: (required) The hostname to configure
   :<json boolean redhat_storage: (optional, default: ``false``) Use the
                                  downstream version of Red Hat Ceph Storage.
   :<json boolean redhat_use_cdn: (optional, default: ``true``) Use the Red Hat
                                  CDN and subscription-manager to install Red
                                  Hat Ceph Storage. This assumes the node is
                                  already registered with subscription-manager.
                                  If ``false``, Red Hat Ceph Storage will be
                                  installed by using repos that must have
                                  already been created on the node.
   :<json boolean verbose: (optional, default: ``false``) Increase the
                           verbosity when calling ansible.

.. http:post:: /api/osd/configure/

   This endpoint supports both collocated journals (a journal in the same
   device as an OSD) and using a raw (separate) journal device for OSDs.

   **Request**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "conf": {"global": {"auth supported": "cephx"}},
          "devices": {"/dev/sdb":"/dev/sdc"},
          "fsid": "deedcb4c-a67a-4997-93a6-92149ad2622a",
          "host": "osd1.example.com",
          "journal_size": 0,
          "cluster_name": "my-ceph-cluster",
          "cluster_network": "192.0.2.0/24",
          "public_network": "198.51.100.0/24",
          "redhat_storage": false,
          "monitors": [{"host": "mon0.host", "interface": "eth1"}, {"host": "mon1.host", "address": "10.0.0.1"}],
          "verbose": false,
      }

   :<json object conf: (optional, default: ``null``) An object that maps
                       ceph.conf sections (only global, mon, osd, rgw, mds
                       allowed) to keys and values. Anything defined in this
                       mapping will override existing settings.
   :<json object|array devices: (required) A mapping of OSD device to Journal
                          like device: {"device": "journal"} (when the journal
                          is separate from the OSD) or ["/dev/sdb", "/dev/sdc"]
                          for collocated OSDs and Journals.
   :<json string fsid: (required) The ``fsid`` for the cluster
   :<json string host: (required) The hostname to configure
   :<json int journal_size: (required) The size to use for the journal
   :<json string public_network: (required) The public network subnet for the
                                 cluster (in `CIDR`_ notation).
   :<json string cluster_network: (optional, default: ``public_network``) The
                                  network subnet exposed to cluster clients (in
                                  `CIDR`_ notation).
   :<json boolean redhat_storage: (optional, default: ``false``) Use the
                                  downstream version of Red Hat Ceph Storage.
   :<json array monitors: (required) The monitors for the cluster you want to
                          add this OSD to.  Provide a list of objects
                          representing the monitor host and its ``interface``
                          or ``address``.
   :<json boolean verbose: (optional, default: ``false``) Increase the
                           verbosity when calling ansible.
   :<json string cluster_name: (optional, default: ``ceph``) Provide a custom
                               name for the ceph cluster.

For collocated journals:

   **Request**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "conf": {"global": {"auth supported": "cephx"}},
          "devices": ["/dev/sdb", "/dev/sdc"],
          "fsid": "deedcb4c-a67a-4997-93a6-92149ad2622a",
          "host": "osd1.example.com",
          "journal_size": 0,
          "cluster_name": "my-ceph-cluster",
          "cluster_network": "192.0.2.0/24",
          "public_network": "198.51.100.0/24",
          "redhat_storage": false,
          "monitors": [{"host": "mon0.host", "interface": "eth1"}, {"host": "mon1.host", "address": "10.0.0.1"}],
          "verbose": false,
      }


Journals
--------
Journals can be collocated on the same device as the data or created
on a dedicated device.

If you wish to use a dedicated journal device then the journals are defined as
devices and are "mapped" in a JSON object. The object maps a device to a journal.
Any one journal can be used for more than one device. For example, for
a ``/dev/sdx`` journal device one can do::

    ...
    "devices": {"/dev/sdb": "/dev/sdx", "/dev/sdc": "/dev/sdx"}
    ...

That example would use the journal ``/dev/sdx`` for both ``/dev/sdb`` and
``/dev/sdc``

If you wish to collocate your journals with the data then the journals are defined
as devices and given in an array. For example::

    ...
    "devices": ["/dev/sdb", "/dev/sdc"]
    ...



``rgw``
=======

.. http:post:: /api/rgw/install/

   Start the installation process for RGW host(s)

   **Response**:

   .. sourcecode:: http

     HTTP/1.1 200 OK
     Content-Type: application/json

     {
         "endpoint": "/api/rgw/install/",
         "succeeded": false,
         "stdout": null,
         "started": null,
         "exit_code": null,
         "ended": null,
         "command": null,
         "stderr": null,
         "identifier": "47f68862-a96b-4ac6-be07-71726b595793"
     }

   **Request**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "host": "rgw1.example.com",
          "redhat_storage": false,
          "redhat_use_cdn": true,
          "verbose": false,
      }

   :<json string hosts: (required) The hostname to install
   :<json boolean redhat_storage: (optional, default: ``false``) Use the
                                  downstream version of Red Hat Ceph Storage.
   :<json boolean redhat_use_cdn: (optional, default: ``true``) Use the Red Hat
                                  CDN and subscription-manager to install Red
                                  Hat Ceph Storage. This assumes the node is
                                  already registered with subscription-manager.
                                  If ``false``, Red Hat Ceph Storage will be
                                  installed by using repos that must have
                                  already been created on the node.
   :<json boolean verbose: (optional, default: ``false``) Increase the
                           verbosity when calling ansible.


.. http:post:: /api/rgw/configure/

   This endpoint configures a Rados Gateway node.

   **Request**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "cluster_name": "ceph",
        "cluster_network": "192.0.2.0/24",
        "conf": {"global": {"auth supported": "cephx"}},
        "fsid": "deedcb4c-a67a-4997-93a6-92149ad2622a",
        "host": "rgw1.example.com",
        "public_network": "198.51.100.0/24",
        "monitors": [{"host": "mon0.host", "interface": "eth1"}, {"host": "mon1.host", "address": "10.0.0.1"}],
        "radosgw_civetweb_bind_ip": "10.0.1.1",
        "radosgw_civetweb_num_threads": 50,
        "radosgw_civetweb_port": 80,
        "radosgw_civetweb_port": 8080,
        "radosgw_dns_name": "rgw1.example.com",
        "radosgw_dns_s3website_name": "rgw1.example.com",
        "radosgw_keystone": false,
        "radosgw_keystone_accepted_roles": ["Member", "_member_",  "admin"],
        "radosgw_keystone_admin_domain": "default",
        "radosgw_keystone_admin_password": "admin-secret",
        "radosgw_keystone_admin_tenant": "tenant",
        "radosgw_keystone_admin_token": "secret",
        "radosgw_keystone_admin_user": "admin",
        "radosgw_keystone_api_version": 3,
        "radosgw_keystone_auth_method": "admin_token",
        "radosgw_keystone_revocation_internal": 900,
        "radosgw_keystone_ssl": true,
        "radosgw_keystone_token_cache_size": 10000,
        "radosgw_keystone_url": "http://192.168.0.1:35357",
        "radosgw_nss_db_path": "/var/lib/ceph/radosgw/ceph-radosgw.rgw1/nss",
        "radosgw_resolve_cname": false,
        "radosgw_s3_auth_use_keystone": "true",
        "radosgw_static_website": false,
        "radosgw_usage_log": false,
        "radosgw_usage_log_flush_threshold": 1024,
        "radosgw_usage_log_tick_interval": 30,
        "radosgw_usage_max_shards": 32,
        "radosgw_usage_max_user_shards": 1,
        "redhat_storage": false,
        "verbose": false,
      }

   :<json string cluster_name: (optional, default: ``ceph``) Provide a custom
                               name for the ceph cluster.
   :<json string cluster_network: (optional, default: ``public_network``) The
                                  network subnet exposed to cluster clients (in
                                  `CIDR`_ notation).
   :<json object conf: (optional, default: ``null``) An object that maps
                       ceph.conf sections (only global, mon, osd, rgw, mds
                       allowed) to keys and values. Anything defined in this
                       mapping will override existing settings.
   :<json string fsid: (required) The ``fsid`` for the cluster
   :<json string host: (required) The hostname to configure
   :<json string public_network: (required) The public network subnet for the
                                cluster (in `CIDR`_ notation).
   :<json array monitors: (required) The monitors for the cluster you want to
                          add this RGW server to.  Provide a list of objects
                          representing the monitor host and its ``interface``
                          or ``address``.
   :<json string radosgw_civetweb_bind_ip: (optional) The address to bind to. Defaults to
                                           the default IPV4 system address
   :<json integer radosgw_civetweb_num_threads: (optional, default: 50)
   :<json integer radosgw_civetweb_port: (optional, default: 8080)
   :<json string radosgw_dns_name: (optional) Subdomains used by RGW. See
                                   http://ceph.com/docs/master/radosgw/config/#enabling-subdomain-s3-calls
   :<json string radosgw_dns_s3website_name: Subdomain used by radosgw for website bucket hosting.
   :<json boolean radosgw_keystone: (optional, default: false)
   :<json array radosgw_keystone_accepted_roles: (optional)
   :<json string radosgw_keystone_admin_domain: (optional)
   :<json string radosgw_keystone_admin_password: (optional)
   :<json string radosgw_keystone_admin_tenant: (optional)
   :<json string radosgw_keystone_admin_token: (optional)
   :<json string radosgw_keystone_admin_user: (optional)
   :<json integer radosgw_keystone_api_version: (optional)
   :<json string radosgw_keystone_auth_method: (optional)
   :<json integer radosgw_keystone_revocation_internal: (optional)
   :<json boolean radosgw_keystone_ssl: (optional)
   :<json integer radosgw_keystone_token_cache_size: (optional)
   :<json string radosgw_keystone_url: (optional)
   :<json string radosgw_nss_db_path: (optional)
   :<json boolean radosgw_resolve_cname: (optional)
   :<json boolean radosgw_s3_auth_use_keystone: (optional)
   :<json boolean radosgw_static_website: (optional)
   :<json boolean radosgw_usage_log: (optional)
   :<json string radosgw_usage_log_flush_threshold: (optional)
   :<json integer radosgw_usage_log_tick_interval: (optional)
   :<json integer radosgw_usage_max_shards: (optional)
   :<json integer radosgw_usage_max_user_shards: (optional)
   :<json boolean redhat_storage: (optional, default: ``false``) Use the
                                  downstream version of Red Hat Ceph Storage.
   :<json boolean redhat_use_cdn: (optional, default: ``true``) Use the Red Hat
                                  CDN and subscription-manager to install Red
                                  Hat Ceph Storage. This assumes the node is
                                  already registered with subscription-manager.
                                  If ``false``, Red Hat Ceph Storage will be
                                  installed by using repos that must have
                                  already been created on the node.
   :<json boolean verbose: (optional, default: ``false``) Increase the
                           verbosity when calling ansible.


``status``
==========

.. http:get:: /api/status/

   Get the system status for the service. Performs checks against different
   required systems and return an HTTP 500 error status code with a message.

   **Response**:

   .. sourcecode:: http

     HTTP/1.1 500 Internal Server Error
     Content-Type: application/json

     {"message": "RabbitMQ is not running or not reachable"}

  :statuscode 500: Server Error (see :ref:`server_errors`)

.. _server_errors:

Known Server Errors
-------------------
These are possible server errors and failures that are handled by the
application itself. Once handled the server will reply with a JSON body and
a single ``message`` key.

No Celery worker running:

  .. sourcecode:: http

     HTTP/1.1 500 Internal Server Error
     Content-Type: application/json

     {"message": "No running Celery worker was found"}

Missing Ansible:

  .. sourcecode:: http

     HTTP/1.1 500 Internal Server Error
     Content-Type: application/json

     {"message": "Could not find ansible in system paths"}

RabbitMQ connection errors:

  .. sourcecode:: http

     HTTP/1.1 500 Internal Server Error
     Content-Type: application/json

     {"message": "Error connecting to RabbitMQ"}

RabbitMQ is not running:

  .. sourcecode:: http

     HTTP/1.1 500 Internal Server Error
     Content-Type: application/json

     {"message": "RabbitMQ is not running or not reachable"}

Database connectivity:

  .. sourcecode:: http

     HTTP/1.1 500 Internal Server Error
     Content-Type: application/json

     {"message": "Could not connect or retrieve information from the database"}



.. _CIDR: https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing
