#!/usr/bin/env bash

set -ex

if [ -z"/JS8" ]; then
    export JSBASE="/JS8/opt/jumpscale8"
    export TMPDIR="/JS8/tmp"
    export CFGDIR="/JS8/optvar/cfg/jumpscale/"
    mkdir -p $JSBASE
else
    if [ "$(uname)" == "Darwin" ]; then
        export TMPDIR="$HOME/tmp"
        export JSBASE="$HOME/opt/jumpscale8"
        export CFGDIR="$HOME/optvar/cfg/jumpscale/"
    fi
fi

#TODO: *1 need to do cleanup for ubuntu as well

rm -f $TMPDIR/jsinstall_systemcomponents_done
rm -f $CFGDIR/done.yaml
