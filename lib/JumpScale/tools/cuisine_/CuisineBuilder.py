
from JumpScale import j
import os

import socket

from ActionDecorator import ActionDecorator
class actionrun(ActionDecorator):
    def __init__(self,*args,**kwargs):
        ActionDecorator.__init__(self,*args,**kwargs)
        self.selfobjCode="cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.builder"


class CuisineBuilder(object):

    def __init__(self,executor,cuisine):
        self.executor=executor
        self.cuisine=cuisine
        self.bash=self.cuisine.bash
        self._gopath=None


    @property
    def GOPATH(self):
        if self._gopath==None:
            if not "GOPATH" in self.bash.environ:
                self.cuisine.installerdevelop.golang()
            self._gopath=   self.bash.environ["GOPATH"]
        return self._gopath
    

    #@todo (*1*) installer for golang
    #@todo (*1*) installer for caddy
    #@todo (*1*) installer for etcd
    #@todo (*1*) installer for skydns
    #@todo (*1*) installer for aydostor

    def installMongo(self, start=True):
        j.actions.setRunId("installMongo")
        rc, out = self.executor.execute('which mongod', die=False)
        if out:
            print('mongodb is already installed')
        appbase = '/usr/local/bin'

        def getMongo(appbase):
            if j.core.platformtype.myplatform.isLinux():#@todo better platform mgmt
                url = 'https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu1404-3.2.1.tgz'
            elif sys.platform.startswith("OSX"): #@todo better platform mgmt
                url = 'https://fastdl.mongodb.org/osx/mongodb-osx-x86_64-3.2.1.tgz'
            #@todo arm
            else:
                # @TODO (*3*) add support for other platforms
                return
            tarpath = j.sal.fs.joinPaths(j.dirs.tmpDir, 'mongodb.tgz')
            j.sal.nettools.download(url, tarpath)
            tarfile = j.tools.tarfile.get(tarpath)
            tarfile.extract(j.dirs.tmpDir)
            extracted = j.sal.fs.walk(j.dirs.tmpDir, pattern='mongodb*', return_folders=1, return_files=0)[0]
            j.sal.fs.copyDirTree(j.sal.fs.joinPaths(extracted, 'bin'), appbase)
            j.sal.fs.createDir('/data/db')

        def startMongo(appbase):
            j.sal.tmux.executeInScreen("main", screenname="mongodb", cmd="mongod", user='root')

        getmongo = j.actions.add(getMongo, args={'appbase': appbase})
        if start:
            j.actions.add(startMongo, args={'appbase': appbase}, deps=[getmongo])
        j.actions.run()


    @actionrun(action=True)
    def findPiNodesAndPrepareJSDevelop(self):
        pass


    @actionrun(action=True)
    def skydns(self):
        C="""
        go get github.com/skynetservices/skydns
        cd $GOPATH/src/github.com/skynetservices/skydns
        go build -v
        """
        self.GOPATH #make sure env's are set & golang installed
        C=self.bash.replaceEnvironInText(C)
        import ipdb
        ipdb.set_trace()



    @actionrun(action=True)
    def installJSDevelop(self):

        self.base()
        self.pythonDevelop()
        self.pip()


        if reset:
            j.actions.reset("installer")

        def cleanNode(cuisineid):
            """
            make node clean e.g. remove redis, install tmux, stop js8, unmount js8
            """
            cuisine=j.tools.cuisine.get(cuisineid)
            C = """
            set +ex
            pskill redis-server #will now kill too many redis'es, should only kill the one not in docker
            pskill redis #will now kill too many redis'es, should only kill the one not in docker
            umount -fl /optrw
            # apt-get remove redis-server -y
            rm -rf /overlay/js_upper
            rm -rf /overlay/js_work
            rm -rf /optrw
            js8 stop
            pskill js8
            umount -f /opt
            apt-get install tmux fuse -y
            """
            cuisine.run_script(C)
            # cuisine.package.remove("redis-server")
            # cuisine.package.remove("redis")



    def __str__(self):
        return "cuisine.installer:%s:%s"%(self.executor.addr,self.executor.port)

    __repr__=__str__



C='''
#!/bin/bash
set -e
source /bd_build/buildconfig
set -x


apt-get update

$minimal_apt_get_install libpython3.5-dev python3.5-dev libffi-dev gcc build-essential autoconf libtool pkg-config libpq-dev
$minimal_apt_get_install libsqlite3-dev
#$minimal_apt_get_install net-tools sudo

cd /tmp
sudo rm -rf brotli/
git clone https://github.com/google/brotli.git
cd /tmp/brotli/
python setup.py install
cd tests
make
cd ..
cp /tmp/brotli/tools/bro /usr/local/bin/
rm -rf /tmp/brotli

#DANGEROUS TO RENAME PYTHON
#rm -f /usr/bin/python
#rm -f /usr/bin/python3
#ln -s /usr/bin/python3.5 /usr/bin/python
#ln -s /usr/bin/python3.5 /usr/bin/python3


cd /tmp
rm -rf get-pip.py
wget https://bootstrap.pypa.io/get-pip.py
python3.5 get-pip.py

cd /tmp
git clone https://github.com/jplana/python-etcd.git
cd python-etcd
python3.5 setup.py install


pip install 'cython>=0.23.4' git+git://github.com/gevent/gevent.git#egg=gevent

pip install paramiko

pip install msgpack-python
pip install redis
pip install credis
pip install aioredis

pip install mongoengine

pip install bcrypt
pip install blosc
pip install certifi
pip install docker-py

pip install gitlab3
pip install gitpython
pip install html2text

# pip install pysqlite
pip install click
pip install influxdb
pip install ipdb
pip install ipython --upgrade
pip install jinja2
pip install netaddr

pip install reparted
pip install pytoml
pip install pystache
pip install pymongo
pip install psycopg2
pip install pathtools
pip install psutil

pip install pytz
pip install requests
pip install sqlalchemy
pip install urllib3
pip install zmq
pip install pyyaml
pip install websocket
pip install marisa-trie
pip install pylzma
pip install ujson
pip install watchdog
'''        
        # self.actions.


