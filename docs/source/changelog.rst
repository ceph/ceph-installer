
changelog
=========

v1.3.0 (2017-04-11)
-------------------

- Add RGW support.

- Improve error message for missing /etc/os-release.

- Avoid unicode errors when using the cli.

- Improve tests to cover more scenarios.

- Docs: further explaination of journal configurations.

- Docs: fix rendering issue in /api/osd/configure docs.

v1.2.2 (2017-01-27)
-------------------

- Allows remote request to the /api/agent/ endpoint

v1.2.1 (2017-01-24)
-------------------

- Restricts POST, PUT and DELETE requests to local requests only.

v1.2.0 (2017-01-17)
-------------------

- Support for collocated journals when configuring OSDs

v1.1.0 (2016-12-19)
-------------------

- Support for v2.1.0 of ceph-ansible.

- Many RPM packaging improvements.

- Support for using systemd for dev deployments instead of circus.

- Includes a functional testing scenario.

v1.0.15 (2016-08-09)
--------------------

- RPM packaging: Fix more SELinux AVC denials.

- RPM packaging: Set ``ceph_installer_t`` SELinux domain to permissive. We have
  still found various AVC denials when running Skyring (Tendrl) with SELinux in
  enforcing mode. To make sure ceph-installer works while we fix the remaining
  issues with the policies, we are going to set the entire ceph_installer_t
  domain to permissive.

  With this change, the ceph-installer service still runs confined, but AVC
  denials will not prevent the service from operating.

  See https://lwn.net/Articles/303216/ for background on permissive SELinux
  domains.


v1.0.14 (2016-07-13)
--------------------

- RPM packaging: Fix SELinux AVC denial when setting up a cluster and SELinux
  is in enforcing mode.


v1.0.13 (2016-07-12)
--------------------

- RPM packaging: Add SELinux policy, and run pecan and celery processes
  confined.

- Fix setup script shebang to be simply "#!/bin/bash". Prior to this change,
  executing the script via the shebang would lead to an error.

- RPM packaging: don't allow Ansible 2 or above, since we've only tested with
  Ansible 1.9.


v1.0.12 (2016-06-10)
--------------------

- RPM packaging: silence output from the "yum install ceph-installer" command.

- Build cleanups.


v1.0.11 (2016-05-18)
--------------------

- Sets CELERYD_CONCURRENCY=1 to ensure there is only one
  celery worker running. We need this to ensure tasks run
  sequentially.


v1.0.10 (2016-05-11)
--------------------
- Adds a man page for the ``ceph-installer`` cli

- Now requires ceph-ansible >= 1.0.5

v1.0.9 (2016-05-09)
-------------------
- Create the necessary SSH keys on app startup.
- Fix an issue where a subprocess couldn't communicate with stdin when using
  ``subprocess.Popen``
- No longer create SSH keys per request on ``/setup/key/``


v1.0.8 (2016-05-06)
-------------------
- Include request information in tasks (available with JSON on ``/api/tasks/``)


v1.0.7 (2016-05-04)
-------------------
- The ``/setup/`` shell script now ensure that Python 2 is installed on
  Ubuntu distros.

- Add additional server-side logging when ``ssh-keygen`` fails during the
  ``/setup/key/`` API call.

- Several small doc updates: remove references to un-implemented callbacks,
  correct the type of ``cluster_name`` (it's a string).

- Add trailing newline to the inventory files that ceph-installer passes
  internally to Ansible. This is not a user-visible change; it just makes it
  easier for developers to debug the auto-generated inventory files.


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
