#!/usr/bin/env bash
set -ex

pip install nose
# copy the tests from the repo dir to a tmp dir
cp -r /opt/code/github/jumpscale/jumpscale_core8/tests /tmp/
cp /opt/code/github/jumpscale/jumpscale_core8/install/InstallTools.py /opt/code/github/jumpscale/jumpscale_core8/lib/JumpScale/
nosetests --with-xunit  /tmp/tests || true
rm -rf /tmp/tests
rm -f /opt/code/github/jumpscale/jumpscale_core8/lib/JumpScale/InstallTools.py
