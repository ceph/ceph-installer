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
The configuration step for any node type (rgw, mon, osd, etc...) is *required* to
be per node. It is up to the caller to handle domain logic.

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

* RabbitMQ
* Ansible

Application requirements:

* pecan
* celery
* sqlalchemy
* gunicorn
* notario
* pecan-notario


Creating a cluster
------------------
To create a cluster there are a few steps involved. There is no single step to
get everything done as many different requirements and restrictions are
applied. Having granular steps allows the client to be able to handle any kind
of logic as the process progresses.

The following example assumes one monitor host ("mon.host") and two OSD hosts
with one device each ("osd1.host" and "osd2.host"). It also assumes the
installer ("installer.host") will be running on the same network and will be
reachable over HTTP from and to the other nodes.

1.- Bootstrap on each remote host (mon.host, osd1.host, and osd2.host)::

    wget http://installer.host/setup/ | sudo bash

2.- Install monitor:

request::

    curl -d '{"hosts": ["mon1.host"], "redhat_storage": true}' -X POST http://installer.hosts/api/mon/install/

response::

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

Note: the identifier can be immediately used get task metadata information::

    curl http:://installer.host/api/tasks/47f60562-a96b-4ac6-be07-71726b595793/
    {
        "endpoint": "/api/mon/install/",
        "succeeded": false,
        "stdout": null,
        "started": "2016-02-15 14:24:06.414728",
        "exit_code": null,
        "ended": null,
        "command": "/usr/local/bin/ansible-playbook /tmp/ceph-ansible/site.yml -i /var/folders/t8/smzdykh12h39f8r0vwv5vzf00000gn/T/47f60562-a96b-4ac6-be07-71726b595793__ilpiv --extra-vars {\"ceph_stable\": true} --tags package-install",
        "stderr": null,
        "identifier": "47f60562-a96b-4ac6-be07-71726b595793"
    }

3.- Install OSDs:

request::
    curl -d '{"hosts": ["osd1.host", "osd2.host"], "redhat_storage": true}' -X POST http://installer.hosts/api/osd/install/

response::

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


Task metadata for the previous request is then available at::

    curl http:://installer.host/api/tasks/03965afd-6ae3-40e5-9530-3ac677a43226/


4.- Configure monitor:

request::
    curl -d '{"host": "mon1.host", "monitor_interface": "eth0", "fsid": "deedcb4c-a67a-4997-93a6-92149ad2622a"}' -X POST http://installer.hosts/api/osd/install/

response::

    {
        "endpoint": "/api/mon/configure/",
        "succeeded": false,
        "stdout": null,
        "started": null,
        "exit_code": null,
        "ended": null,
        "command": null,
        "stderr": null,
        "identifier": "4fe75438-1c76-40f9-b39c-9dbe78af28ed"
    }

Task metadata for the previous request is then available at::

    curl http:://installer.host/api/tasks/4fe75438-1c76-40f9-b39c-9dbe78af28ed/


4.- Configure OSDs:
Note that we are using ``journal_collocate`` flag to indicate we are going to
collocate the journal in the same device as the OSD. This is *not ideal* and
*not recommended for production use*, but it makes example setups easier to
describe.

request::
    curl -d '{"host": "osd1.host", "devices": ["/dev/sdb/"], "journal_collocate": true, "fsid": "deedcb4c-a67a-4997-93a6-92149ad2622a"}' -X POST http://installer.hosts/api/osd/configure/

response::

    {
        "endpoint": "/api/mon/configure/",
        "succeeded": false,
        "stdout": null,
        "started": null,
        "exit_code": null,
        "ended": null,
        "command": null,
        "stderr": null,
        "identifier": "4af5189e-0e6c-4aa3-930c-b0ca6adb2545"
    }

Task metadata for the previous request is then available at::

    curl http:://installer.host/api/tasks/4af5189e-0e6c-4aa3-930c-b0ca6adb2545/


request::
    curl -d '{"host": "osd2.host", "devices": ["/dev/sdc/"],
    "journal_collocate": true}' -X POST
    http://installer.hosts/api/osd/configure/

response::

    {
        "endpoint": "/api/mon/configure/",
        "succeeded": false,
        "stdout": null,
        "started": null,
        "exit_code": null,
        "ended": null,
        "command": null,
        "stderr": null,
        "identifier": "f248c190-4bb1-47d5-9188-c98434419f39"
    }

Task metadata for the previous request is then available at::

    curl http:://installer.host/api/tasks/f248c190-4bb1-47d5-9188-c98434419f39/


Once all tasks have completed correctly, the cluster should be up and in
healthy state.

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

Other possible responses for known system failures may include:

* ``{"message": "Could not find ansible in system paths"}``
* ``{"message": "No running Celery worker was found"}``
* ``{"message": "Error connecting to RabbitMQ"}``
* ``{"message": "RabbitMQ is not running or not reachable"}``
* ``{"message": "Could not connect or retrieve information from tha database"}``


``tasks``
=========

A task is created when an action on a remote node is triggered (for example to
install packages on a monitor node).  They can be used to track the progress of
the operation, like installing or configuring a remote node.

Tasks contain metadata for these calls. This metadata includes items like: start
time, end time, success, stderr, stdout

It provides two ways to consume the status of a given task:

* polling
* callback

Callback System
---------------
Each API endpoint will allow an optional "callback" key with a URL value. That
URL will be triggered when a task has finished (this includes error, success,
or failure states).

The request for the callback URL will be an HTTP POST with the full JSON
metadata of the task.


Polling
-------
As soon as a call is performed and conditions are met for provisioning on
a remote node a "task" is created. This means the information is not atomic, it
is available as soon as the call proceeds to a remote node interaction and
information gets updated as the task completes.

When a task is not done it will have a ``null`` value for the ``ended`` key, will
default to ``"succeeded": "false"`` and it will have a ``completed`` key that will
be ``true`` when the task has finished.  These tasks have an unique identifier.
The endpoints *will always return a 200 when they are available*.

Polling is not subject to handle state with HTTP status codes (e.g. 304)


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
        'redhat_storage': False,
        'callback': 'http://example.com/task-callback/'
    }


``/api/mon/configure/``
-----------------------
* ``POST``: Configure monitor(s)
Body ::

    {
        'host': 'mon1.example.com',
        'monitor_interface': 'eth0',
        'fsid': '',
        'monitor_secret': '',
        'callback': 'http://example.com/task-callback/'
    }

The fields ``fsid`` and ``monitor_secret`` are not required. If not provided, they will
be autogenerated and that value will be used.


``osd``
=======


``/api/osd/install/``
---------------------
* ``POST``: Start the installation process for monitor(s)
Body ::

    {
        'hosts': ['osd1.example.com', 'osd2.example.com'],
        'redhat_storage': False,
        'callback': 'http://example.com/task-callback/'
    }


``/api/osd/configure/``
-----------------------
* ``POST``: Configure OSD(s)
Body ::

    {
        'devices': ['/dev/sdb'],
        'hostname': 'osd1.example.com',
        'journal_collocate': True,
        'callback': 'http://example.com/task-callback/'
    }


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
        'redhat_storage': False,
        'callback': 'http://example.com/task-callback/'
    }


``/api/rgw/configure/``
-----------------------
* ``POST``: Configure OSD(s)
``name`` is optional, will default to ``rgw.$short-hostname``, using the
examples below, that would be ``rgw.node1`` and ``rgw.node2``. It is allowed to
specify a ``name`` to alter this default behavior.

Body ::

    {
        'name': 'main',
        'hostname': 'rgw1.example.com',
        'callback': 'http://example.com/task-callback/'
    }


``calamari``
============

``/api/calamari/install/``
--------------------------
* ``POST``: Start the installation process for calamari
Body ::

    {
        'host': ['calamari.example.com'],
        'redhat_storage': False,
        'callback': 'http://example.com/task-callback/'
    }

``/api/calamari/configure/``
----------------------------
# TODO
