#!/usr/bin/env bash
set -ex

pip install nose
# copy the tests from the repo dir to a tmp dir
cp -r /opt/code/github/jumpscale/jumpscale_core8/tests /tmp/
nosetests --with-xunit  /tmp/tests
rm -rf /tmp/tests
