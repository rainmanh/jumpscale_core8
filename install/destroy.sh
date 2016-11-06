#!/usr/bin/env bash
rm -rf /opt/jumpscale8
rm -rf /JS8/opt/jumpscale8
rm -rf /JS8/optvar/

source clean.sh

set -ex

rm -rf $CODEDIR/github/jumpscale/ays_jumpscale8/
rm -rf $CODEDIR/github/jumpscale/jumpscale_core8/
rm -rf $CODEDIR/github/jumpscale/jumpscale_portal8/
