#!/usr/bin/env bash
set -e

export STARTDIR=$PWD

reset='true'
while getopts ":kh" opt; do
    case $opt in
      k)
        reset='false'
        ;;
      h)
        echo "Usage install.sh:
        -k keep don't remove jumpscale directory if it exists before installation
        "
        exit 44
    esac
done

if [ $reset == "true" ]; then
    rm -rf /opt/jumpscale8
fi


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
export AYSGIT='https://github.com/Jumpscale/ays_jumpscale8'
export AYSBRANCH='master'

if [ -z"/JS8" ]; then
    export JSBASE="/JS8/opt/jumpscale8"
    export TMPDIR="/JS8/tmp"
    mkdir -p $JSBASE
else
    if [ "$(uname)" == "Darwin" ]; then
        export TMPDIR="$HOME/tmp"
        export JSBASE="$HOME/opt/jumpscale8"
    fi
fi

mkdir -p $TMPDIR
cd $TMPDIR

function osx_install {
    brew install curl
    brew install python3
    brew install redis
    # brew install git
    pip3 install --upgrade pip setuptools
    pip3 install --upgrade ipdb
    pip3 install --upgrade requests
    pip3 install --upgrade paramiko
    pip3 install --upgrade watchdog
    pip3 install --upgrade mongoengine
    pip3 install --upgrade hiredis
    # pip3 install dulwich
    pip3 install --upgrade gitpython
    pip3 install --upgrade click
    pip3 install --upgrade ptpython
    pip3 install --upgrade pymux
    pip3 install --upgrade ptpdb
    pip3 install --upgrade http://carey.geek.nz/code/python-fcrypt/fcrypt-1.3.1.tar.gz
    pip3 install --upgrade uvloop
}

if [ "$(uname)" == "Darwin" ]; then
    # Do something under Mac OS X platform
    #echo 'install brew'
    #ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    export LANG=C; export LC_ALL=C
    # osx_install


elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    # export LC_ALL='C.UTF-8'
    locale-gen en_US.UTF-8
    export LANG=en_US.UTF-8
    export LC_ALL=en_US.UTF-8
    dist=''
    dist=`grep DISTRIB_ID /etc/*-release | awk -F '=' '{print $2}'`
    if [ "$dist" == "Ubuntu" ]; then
        echo "found ubuntu"
        apt-get install mc curl git ssh python3.5 -y
        rm -f /usr/bin/python
        rm -f /usr/bin/python3
        ln -s /usr/bin/python3.5 /usr/bin/python
        ln -s /usr/bin/python3.5 /usr/bin/python3
        apt-get install python3-pip python3-click -y
        pip3 install --upgrade uvloop
    elif [ -f "/etc/slitaz-release" ]; then
      echo "found slitaz"
      tazpkg get-install curl
      tazpkg get-install git
      tazpkg get-install python3.5
    fi

    if [ -z $JSBASE ]; then
        export JSBASE='/opt/jumpscale8'
    fi
    export TMPDIR=/tmp
elif [ "$(expr substr $(uname -s) 1 9)" == "CYGWIN_NT" ]; then
    # Do something under Windows NT platform
    export LANG=C; export LC_ALL=C
    lynx -source rawgit.com/transcode-open/apt-cyg/master/apt-cyg > apt-cyg
    install apt-cyg /bin
    apt-cyg install curl
    apt-cyg install openssl-devel
    apt-cyg install wget
    apt-cyg install python3
    apt-cyg install make
    apt-cyg install libffi-devel
    apt-cyg install unzip

    python3 -m ensurepip
    ln -sf /usr/bin/python3 /usr/bin/python
    apt-cyg install git

    pip3 install cryptography==1.4
    pip3 install --upgrade paramiko
    pip3 install --upgrade pip setuptools
    pip3 install --upgrade ipdb
    pip3 install --upgrade requests
    pip3 install --upgrade watchdog
    pip3 install --upgrade mongoengine
    # pip3 install dulwich
    pip3 install --upgrade gitpython
    pip3 install --upgrade click
    pip3 install --upgrade ptpython
    pip3 install --upgrade pymux
    pip3 install --upgrade ptpdb
    pip3 install --upgrade http://carey.geek.nz/code/python-fcrypt/fcrypt-1.3.1.tar.gz

    export TMPDIR=/tmp

    #install redis
    cd $TMPDIR
    rm -rf Redis
    mkdir Redis
    cd Redis
    wget -O Redis-x64-3.2.100.zip https://github.com/MSOpenTech/redis/releases/download/win-3.2.100/Redis-x64-3.2.100.zip
    unzip Redis-x64-3.2.100.zip
    chmod +x redis-server.exe
    cp -f  redis-server.exe /usr/local/bin

    if [ -z"$JSBASE" ]; then
        export JSBASE="$HOME/opt/jumpscale8"
    fi
    mkdir -p $TMPDIR
    cd $TMPDIR
fi


set -ex
branch=${JSBRANCH-master}

cd $STARTDIR

if [ -e"web/bootstrap.py" ]; then
    cp bootstrap.py $TMPDIR/bootstrap.py
    cp InstallTools.py $TMPDIR/InstallTools.py
else
    curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/$branch/install/bootstrap.py > $TMPDIR/bootstrap.py
    curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/$branch/install/InstallTools.py?$RANDOM > $TMPDIR/InstallTools.py
fi


cd $TMPDIR
if [ "${reset}" == "true" ]; then
    python3 bootstrap.py
else
    python3 bootstrap.py --no-reset
fi
