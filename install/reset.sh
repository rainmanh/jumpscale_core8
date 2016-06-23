#!/usr/bin/env bash
rm -rf /opt/jumpscale8

set -ex
#known env variables

#JSBASE : is root where jumpscale will be installed
#SANDBOX : if system will be installed as sanbox or not (1 or 0)
#GITHUBUSER : user used to connect to github
#GITHUBPASSWD : passwd used to connect to github
#JSGIT : root for jumpcale git

#how to set the env vars: below you can find the defaults
# export GITHUBUSER=''
# export GITHUBPASSWD=''
#export SANDBOX=0
#export JSBASE='/opt/jumpscale8'
# export JSGIT='https://github.com/Jumpscale/jumpscale_core8.git'
export PYTHONVERSION='3'

if [ "$(uname)" == "Darwin" ]; then
    export TMPDIR=~/tmp
    export CODEDIR=~/opt/code
    
    if [ -z"$JSBASE" ]; then 
        export JSBASE= "$HOME/opt/jumpscale8"
    fi
    rm -rf $TMPDIR
    mkdir -p $TMPDIR
    cd $TMPDIR
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    dist=''
    dist=`grep DISTRIB_ID /etc/*-release | awk -F '=' '{print $2}'`
    if [ "$dist" == "Ubuntu" ]; then
        echo "found ubuntu"
        rm -f /usr/bin/python
        rm -f /usr/bin/python3
        ln -s /usr/bin/python3.5 /usr/bin/python
        ln -s /usr/bin/python3.5 /usr/bin/python3
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

rm -rf $CODEDIR/github/jumpscale/ays_jumpscale8/
rm -rf $CODEDIR/github/jumpscale/jumpscale_core8/
rm -rf $CODEDIR/github/jumpscale/jumpscale_portal8/

set -ex
rm -rf $JSBASE
