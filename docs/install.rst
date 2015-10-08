Install
=======

Install the ``mariner-installer`` package and its dependencies

We also need to install ``ceph-common`` on the Foreman node to gain
access to ``ceph-authtool`` so that we can seed the monitors with
a cephx key.

CentOS 7
--------
yum -y install https://copr.fedoraproject.org/coprs/trhoden/takora/repo/epel-7/trhoden-takora-epel-7.repo
yum -y install https://copr.fedoraproject.org/coprs/trhoden/mariner-installer/repo/epel-7/trhoden-mariner-installer-epel-7.repo
yum -y install http://yum.puppetlabs.com/puppetlabs-release-el-7.noarch.rpm
yum -y install epel-release http://yum.theforeman.org/releases/1.7/el7/x86_64/foreman-release.rpm
yum -y install http://download.ceph.com/rpm-hammer/el7/noarch/ceph-release-1-1.el7.noarch.rpm
yum -y install mariner-installer ceph-common

RHEL 7
------

subscription-manager repos --enable rhel-7-server-rpms --enable rhel-server-rhscl-7-rpms --enable rhel-7-server-rhceph-1.3-installer-rpms --enable rhel-7-server-rhceph-1.3-tools-rpms
yum -y install rhcs-installer ceph-common

Run
===

Run the ``mariner-installer`` executable::

    mariner-installer

..note: On RHEL systems, run ``rhcs-installer`` instead


