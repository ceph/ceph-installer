Foreman Registration
====================

Nodes need to be registered with Foreman before they can be configured.

To do this, you must install Puppet and configure Puppet to point to your
Foreman server.

CentOS 7
--------

Install Puppet::

    yum -y install puppet


RHEL 7
------

The Puppet RPM is available in the MON, OSD, and Tools repos.  Enable
whichever repos you need for the Ceph daemon you are going to run.  For
example::

    subscription-manager repos --enable rhel-7-server-rhceph-1.3-mon-rpms
    yum -y install puppet


Configure Puppet
----------------

Disable the Puppet agent from running automtically::

    puppet config set --section agent daemonize false

Point your Puppet agent to the foreman server::

    puppet config set --section agent server <FQDN>

Run Puppet agent to register with foreman::

    puppet agent --onetime --test --waitforcert 30 --noop

When the ``puppet agent`` command is run the first time it will pause while
it is waiting for the SSL cert to be signed.  In order to accept this node
into the foreman config, you must use the foreman GUI to sign the request
from the new node.  This is done under ``Infrastructure`` tab in the GUI.
