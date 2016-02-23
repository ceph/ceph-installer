.. creating_a_cluster:

Creating a cluster
==================
To create a cluster there are a few steps involved. There is no single step to
get everything done as many different requirements and restrictions are
applied. Having granular steps allows the client to be able to handle any kind
of logic as the process progresses.

The following example assumes one monitor host ("mon.host") and two OSD hosts
with one device each ("osd1.host" and "osd2.host"). It also assumes the
installer ("installer.host") will be running on the same network and will be
reachable over HTTP from and to the other nodes.

Using callbacks is entirely optional and omitted from the examples below.
Callbacks are an easier way to deal with asynchronous reports for requests and
it is implemented with the ``"callback"`` key in most JSON POST requests.

1.- Bootstrap on each remote host (mon.host, osd1.host, and osd2.host)::

    wget http://installer.host/setup/ | sudo bash

**Security**: the above example retrieves executable code over an
unencrypted protocol and then executes it as root.  You should only
use this approach if you 100% trust your network and your DNS
server.


2.- Install monitor:

request::

    curl -d '{"hosts": ["mon1.host"], "redhat_storage": true}' -X POST http://installer.hosts/api/mon/install/

response:

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

Note: the identifier can be immediately used get task metadata information::

    curl http:://installer.host/api/tasks/47f60562-a96b-4ac6-be07-71726b595793/

response:

  .. sourcecode:: http

     HTTP/1.1 200 OK
     Content-Type: application/json

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

response:

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


Task metadata for the previous request is then available at::

    curl http:://installer.host/api/tasks/03965afd-6ae3-40e5-9530-3ac677a43226/


4.- Configure monitor:

request::

    curl -d '{"host": "mon1.host", "monitor_interface": "eth0", "fsid": "deedcb4c-a67a-4997-93a6-92149ad2622a"}' -X POST http://installer.hosts/api/mon/configure/

response:

  .. sourcecode:: http

     HTTP/1.1 200 OK
     Content-Type: application/json

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
Note that we are using ``journal_collocation`` flag to indicate we are going to
collocate the journal in the same device as the OSD. This is *not ideal* and
*not recommended for production use*, but it makes example setups easier to
describe.

request::

    curl -d '{"host": "osd1.host", "devices": ["/dev/sdb/"], "journal_collocation": true, "fsid": "deedcb4c-a67a-4997-93a6-92149ad2622a"}' -X POST http://installer.hosts/api/osd/configure/

response:

  .. sourcecode:: http

     HTTP/1.1 200 OK
     Content-Type: application/json

     {
         "endpoint": "/api/osd/configure/",
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
    "journal_collocation": true}' -X POST
    http://installer.hosts/api/osd/configure/

response:

  .. sourcecode:: http

     HTTP/1.1 200 OK
     Content-Type: application/json

     {
         "endpoint": "/api/osd/configure/",
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


