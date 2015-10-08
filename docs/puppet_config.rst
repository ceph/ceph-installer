Puppet Config
=============

The next step in using Foreman to deploy Ceph is to configure Puppet with the
needed parameters.  This is done by configuring Smart Variables within the
Foreman GUI.

Import Ceph Puppet modules
--------------------------

To add the Ceph Puppet modules to Foreman, you first need to modify the puppet
modulepath for your ``production`` environment (or whichever puppet environment
you prefer).  Do the following to make the packaged modules necessary for
Ceph deployment available to Puppet and Foreman::

    echo 'modulepath = modules:$basemodulepath:/usr/share/ceph-puppet/modules' > /etc/puppet/environments/production/environment.conf

Then go to Foreman's Configure->"Puppet classes" menu.  From there, click the
"Import from" button, and Foreman should show you the Puppet modules that are
newly available for import into Foreman.  This step needs to be re-run any time
that new modules are added to the system.

Check the box for the modules and add them.

Configure Ceph Parameters
-------------------------

Most of the work to configure Ceph is in the ``ceph::profile::params`` module.

Go to Configure->"Puppet Classes", then click on ``ceph::profile::params``, then
click the "Smart Class Parameter" tab.  Here you will see the parameters that
are available in the Puppet module, and these parameters can be overriden by
Foreman, either globally or on a per-host basis.  More complex overrides are
also possible.

The required parameters that **must** be set are:

* mon host
* mon initial members
* mon key
* fsid
* manage repo (RHEL only)
* client keys (if authentication_type is 'cephx' [default])

It is **recommended** that you also override:

* cluster network
* public network
* release (non-RHEL only)

Note:: On RHEL systems, you **must** set manage repo to False

Generate a new ``fsid`` using ``uuidgen``

Generate a new mon key using ``ceph-authtool --gen-print-key``

``mon host`` is a comma-separated string of IP addresses that the monitors can
be contacted on and will bind to.  These IP addresses must be in the
``public network`` CIDR, and must be available on the hosts used as monitors.

``mon initial members`` is a comma-separated string of FQDNs of the
monitor hosts.

``client keys`` is a hash of cephx keys and their capabilities.  You should use
``ceph-authtool --gen-print-key`` to generate a unique secret for each each cephx
key, and the hash should be as follows::

  client.admin:
    secret: AQAZ2hZWcpGDMRAADx8KLecrH66kE2gLNYbAbQ==
    mode: '0600'
    cap_mon: allow *
    cap_osd: allow *
    cap_mds: allow *
  client.bootstrap-osd:
    secret: AQAz2hZW9jv2HhAADKtXuZX8a5UbHt4uQGmHdw==
    keyring_path: /var/lib/ceph/bootstrap-osd/ceph.keyring
    cap_mon: allow profile bootstrap-osd

**RHEL Only**::

  Go to Configure->"Puppet Classes", then click on ``ceph::params``, then
  check "override" for the ``packages`` parameter.  We need to make the puppet
  module install "ceph-mon" on monitor nodes and "ceph-osd" on OSD nodes.  The
  default packages is just "ceph".

  Set the default value to "ceph-osd".

  Scroll down to "Override for specific hosts", then click "Add matcher value".

  Set the "match" textbox to "fqdn=<fqdn of mon>", and the value textbox to
  "ceph-mon".

  Repeat for each host that is a Ceph Monitor.
