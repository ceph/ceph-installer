
changelog
=========

v1.0.6 (2016-04-29)
-------------------

- When the ``/setup/key/`` controller experiences a failure during the
  ``ssh-keygen`` operation, it will now return both the STDOUT and STDERR
  output from the failed key generation operation. Prior to this change, the
  controller would only return STDERR, and STDOUT was lost. The purpose of
  this change is to make it easier to debug when ``ssh-keygen`` fails.

- The systemd units now cause the ``ceph-installer`` and
  ``ceph-installer-celery`` services to log both STDOUT and STDERR to the
  systemd journal.

1.0.5 (2016-04-19)
------------------

- Properly handle unicode output from ansible runs before storing them as
  a task in the database.

- Prevent the same monitor from being duplicated in ceph.conf by removing it
  from ``monitors`` before calling ceph-ansible.

1.0.4 (2016-04-12)
------------------

- Fixes a bug that did not allow the use of the monitor ``address`` when
  configuring MONS or OSDs.

1.0.3 (2016-04-07)
------------------

- Adds the ability to provide a custom cluster name by using the ``cluster_name``
  parameter when configuring MONs or OSDs.

1.0.2 (2016-03-28)
------------------

- Adds the ability to use ``address`` instead of ``interface`` when configuring
  MONs or OSDs. This replaces the ``monitor_interface`` parameter.

1.0.1 (2016-03-14)
------------------

- Fixes a bug where OSD configure fails when the OSD node being configured
  is also a MON

- Allow values in ceph.conf to be set by using the ``conf`` parameter in the
  api/mon/configure/ and api/osd/configure/ endpoints

- Adds the ability to set the ceph-installer address with the use of an
  environment varaible for the ceph-installer cli.

1.0.0 (2016-03-11)
------------------

- Initial stable release.
