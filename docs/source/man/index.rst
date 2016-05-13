==============
ceph-installer
==============

-------------------------------------------------------------------------
Command line utility to install and configure Ceph using an HTTP REST API
-------------------------------------------------------------------------

:Manual section: 8

Global Options
--------------

-h, --help, help    Show this program's help menu

--log, --logging    Set the level of logging. Acceptable values: debug, warning, error, critical

Environment Variables
---------------------

CEPH_INSTALLER_ADDRESS
    Define the location of the installer.

    Defaults to "http://localhost:8181"

Commands
--------

task
++++


Human-readable task information: stdout, stderr, and the ability to "poll"
a task that waits until the command completes to be able to show the output
in a readable way.

Usage::

    ceph-installer task $IDENTIFIER

Options::

    --poll        Poll until the task has completed (either on failure or success)
     stdout        Retrieve the stdout output from the task
     stderr        Retrieve the stderr output from the task
     command       The actual command used to call ansible
     ended         The timestamp (in UTC) when the command completed
     started       The timestamp (in UTC) when the command started
     exit_code     The shell exit status for the process
     succeeded     Boolean value to indicate if process completed correctly

dev
+++


Deploying the ceph-installer HTTP service to a remote server with ansible.
This command wraps ansible and certain flags to make it easier to deploy
a development version.

Usage::

    ceph-installer dev $HOST

Note: Requires a remote user with passwordless sudo. User defaults to
"vagrant".

Options:

--user        Define a user to connect to the remote server. Defaults  to 'vagrant'
--branch      What branch to use for the deployment. Defaults to 'master'
-vvvv         Enable high verbosity when running ansible

