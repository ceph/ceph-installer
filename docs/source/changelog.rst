
changelog
=========

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
