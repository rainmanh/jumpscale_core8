#!/usr/bin/env bash

set -ex

source resetstate.sh

if [ "$(uname)" == "Darwin" ]; then
    export TMPDIR=~/tmp
    export CODEDIR=~/opt/code

    rm -rf /usr/bin/python3*
    rm -rf /usr/lib/python3*
    rm -rf /usr/local/lib/python3*
    rm -rf /usr/local/bin/python3*

    set +ex
    brew uninstall python3
    set -ex
    brew install python3
    brew linkapps python3

    rm -rf $HOME/tmp
    mkdir -p $TMPDIR
    cd $TMPDIR

elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    dist=''
    dist=`grep DISTRIB_ID /etc/*-release | awk -F '=' '{print $2}'`
    if [ "$dist" == "Ubuntu" ]; then
        echo "found ubuntu"
        rm -rf /usr/bin/python3*
        rm -rf /usr/lib/python3*
        rm -rf /usr/local/lib/python3*
        rm -rf /usr/local/bin/python3*

        apt install python3

    fi
    if [ -z $JSBASE ]; then
        export JSBASE='/opt/jumpscale8'
    fi
    export TMPDIR=/tmp
    export CODEDIR=/opt/code
elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" ]; then
    # Do something under Windows NT platform
    echo 'windows'
    echo "CODE NOT COMPLETE FOR WINDOWS IN install.sh"
    exit
fi
