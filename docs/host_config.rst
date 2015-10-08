Host Config
===========

With high-level Puppet configuration done, it is time to do
host-specific configuration through the Foreman interface.  In
Foreman, go to Hosts->All Hosts.

Mon Config
==========

For each node that is going to be a Ceph Monitor, click the host
FQDN at Hosts->All Hosts, then click the "Edit" button near the
top-right.  Choose the Puppet Classes tab, and use the plus symbol
to expand the "ceph" classes.

Then use the plus symbol to "add" the following classes to the Host::
ceph::profile::params
ceph::profile::mon
**RHEL Only** ceph::params

Click Submit.

OSD Config
==========

For each node that is going to be a Ceph Monitor, click the host
FQDN at Hosts->All Hosts, then click the "Edit" button near the
top-right.  Choose the Puppet Classes tab, and use the plus symbol
to expand the "ceph" classes.

Then use the plus symbol to "add" the following classes to the Host::
ceph::profile::params
ceph::profile::osd
**RHEL Only** ceph::params

Click Submit.

Run Puppet
==========

To actually configure the nodes, go to each host and run::

  puppet agent --onetime --test

**Note**::

  If Foreman is configured for it, you can also use the
  "run puppet" button within the Foreman UI, rather than SSH to each
  host and run Puppet manually.
