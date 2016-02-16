
setup_script = """#!/bin/bash -x -e
if [[ $EUID -ne 0 ]]; then
  echo "You must be a root user or execute this script with sudo" 2>&1
  exit 1
fi

echo "--> creating new user with disabled password: ansible"
useradd -m ceph-installer
passwd -d ceph-installer

echo "--> adding provisioning key to the ansible authorized_keys"
curl -s -L -o ansible.pub {ssh_key_address}
mkdir -p /home/ansible/.ssh
cat ansible.pub >> /home/ansible/.ssh/authorized_keys
chown -R ceph-installer:ceph-installer /home/ansible/.ssh

echo "--> ensuring that ansible user will be able to sudo"
echo "ansible ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/ansible > /dev/null

echo "--> ensuring ansible user does not require a tty"
echo 'Defaults:ansible !requiretty' | sudo tee /etc/sudoers.d/ansible > /dev/null
"""

# Note that the agent_script can't run by itself, it needs to be concatenated
# along the regular setup script
agent_script = """
echo "--> installing and configuring agent"
curl -d '{{"hosts": ["{target_host}"]}}' -X POST {agent_endpoint}
"""
