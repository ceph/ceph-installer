Forman-based Ceph Installer
===========================

The Foreman-based Ceph Installer uses Foreman and Puppet to install and configure a new Ceph Storage Cluster.

The use of Foreman allows for provisioning machines from bare-metal, though this is not yet part of the project.

A Foreman plugin is planned (Mariner) to provide a Ceph specific wizard and interface within Foreman.  Until then
Foreman can be used to manually control Puppet variables to achieve the desired deployment configuration.

The instructions here are specific to Foreman 1.7, and currently support CentOS 7 and RHEL 7.  Instructions for
Ubuntu 14.04 are coming.
