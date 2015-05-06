#!/bin/bash

MODULE_DEST=/etc/puppet/modules

# get modules from git repositories
TAKORA_VERSION="master"

rm -rf /tmp/takora
echo "Cloning Takora repo"
git clone https://github.com/ceph/takora /tmp/takora
pushd /tmp/takora
git reset --hard $TAKORA_VERSION
find /tmp/takora -mindepth 1 -maxdepth 1 -not -path "*.git" -type d -exec cp -pr {} $MODULE_DEST \;
popd
