
setup_script = """#!/bin/bash -x -e
if [[ $EUID -ne 0 ]]; then
  echo "You must be a root user or execute this script with sudo" 2>&1
  exit 1
fi

if [ ! -f /etc/os-release ]; then
    echo "Unable to determine a supported system"
    echo "will not proceed with installation"
    exit 2
fi

source /etc/os-release
if [ "$ID" != "ubuntu" ] && [ "$ID" != "rhel" ]; then
    echo "Unsupported system detected: $ID"
    echo "will not proceed with installation"
    exit 3
fi


if [ "$ID" == "ubuntu" ]; then
    echo "--> Installing Python 2.7 for Ansible"
    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get -y install python
fi

echo "--> creating new user with disabled password: ceph-installer"
useradd -m ceph-installer
passwd -d ceph-installer

echo "--> adding provisioning key to the ceph-installer user authorized_keys"
curl -s -L -o ansible.pub {ssh_key_address}
mkdir -m 700 -p /home/ceph-installer/.ssh
cat ansible.pub >> /home/ceph-installer/.ssh/authorized_keys

echo "--> ensuring correct permissions on .ssh/authorized_keys"
chown -R ceph-installer:ceph-installer /home/ceph-installer/.ssh
chmod 600 /home/ceph-installer/.ssh/authorized_keys

echo "--> ensuring that ceph-installer user will be able to sudo"
# write to it wiping everything
echo "ceph-installer ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/ceph-installer

echo "--> ensuring ceph-installer user does not require a tty"
# and now just append
echo 'Defaults:ceph-installer !requiretty' >> /etc/sudoers.d/ceph-installer
"""

# Note that the agent_script can't run by itself, it needs to be concatenated
# along the regular setup script
agent_script = """
echo "--> installing and configuring agent"
curl -d '{{"hosts": ["{target_host}"]}}' -X POST {agent_endpoint}
"""
