#!/usr/bin/env bash
set -ex

export STARTDIR=$PWD

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

#TO RESET, to develop faster uncomment
rm -f $TMPDIR/jsinstall_systemcomponents_done
rm -f $CFGDIR/done.yaml


mkdir -p $TMPDIR
cd $TMPDIR

function osx_install {
    if [ -e $TMPDIR/jsinstall_systemcomponents_done ] ; then
        echo "NO NEED TO INSTALL CURL/PYTHON/GIT"
    else
        brew install curl
        brew install python3
        brew install git
    fi
}

function pip_install {
    if [ -e $TMPDIR/jsinstall_systemcomponents_done ] ; then
        echo "NO NEED TO INSTALL PIP COMPONENTS"
    else
        pip3 install --upgrade pip setuptools
        pip3 install --upgrade pyyaml
        pip3 install --upgrade asyncio
        pip3 install --upgrade uvloop
        pip3 install --upgrade ipython
    fi
}

if [ "$(uname)" == "Darwin" ]; then
    # Do something under Mac OS X platform
    # echo 'install brew'
    export LANG=C; export LC_ALL=C
    osx_install


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
    apt-cyg install unzip

    python3 -m ensurepip
    ln -sf /usr/bin/python3 /usr/bin/python
    apt-cyg install git

    export TMPDIR=/tmp

    # #install redis
    # cd $TMPDIR
    # rm -rf Redis
    # mkdir Redis
    # cd Redis
    # wget -O Redis-x64-3.2.100.zip https://github.com/MSOpenTech/redis/releases/download/win-3.2.100/Redis-x64-3.2.100.zip
    # unzip Redis-x64-3.2.100.zip
    # chmod +x redis-server.exe
    # cp -f  redis-server.exe /usr/local/bin

    if [ -z"$JSBASE" ]; then
        export JSBASE="$HOME/opt/jumpscale8"
    fi
    mkdir -p $TMPDIR
    cd $TMPDIR
fi

pip_install

touch $TMPDIR/jsinstall_systemcomponents_done

set -ex
branch=${JSBRANCH-master}

cd $STARTDIR

if [ -e "bootstrap.py" ]; then
    cp bootstrap.py $TMPDIR/bootstrap.py
    cp InstallTools.py $TMPDIR/InstallTools.py
    cp dependencies.py $TMPDIR/dependencies.py
else
    curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/$branch/install/bootstrap.py?$RANDOM  > $TMPDIR/bootstrap.py
    curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/$branch/install/InstallTools.py?$RANDOM > $TMPDIR/InstallTools.py
    curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/$branch/install/dependencies.py?$RANDOM > $TMPDIR/dependencies.py
fi


cd $TMPDIR
python3 bootstrap.py
