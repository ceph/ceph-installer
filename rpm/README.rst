Building RPMs
=============
Here are the steps to build an RPM from a Git snapshot (your current
``HEAD``), assuming you're on a CentOS 7 or RHEL 7 host::

    # Enable EPEL
    sudo yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm

    # Install "make" and "fedpkg":
    sudo yum -y install make fedpkg

    # Add your user account to the "mock" group.
    sudo usermod -a -G mock $(whoami)

    # Make the RPM snapshot:
    make rpm

If the build fails, try checking ``root.log`` and ``build.log``, like so::

    tail -n +1 {root,build}.log


This "rpm" directory
====================
This directory contains the mock configuration file for ceph-installer to build
in a mock chroot with all its build-time dependencies.

For more general information about mock, see the project home page at
https://github.com/rpm-software-management/mock/wiki
