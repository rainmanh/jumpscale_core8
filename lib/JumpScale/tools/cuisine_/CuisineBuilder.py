
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



    # @actionrun(action=True)
    # def findPiNodesAndPrepareJSDevelop(self):
    #     pass


    @actionrun(action=True)
    def skydns(self):
        self.GOPATH
        self.cuisine.golang.get("github.com/skynetservices/skydns",action=True)
        self.cuisine.file_copy(j.sal.fs.joinPaths(self.GOPATH, 'bin', 'skydns'),'/opt/jumpscale8/bin',action=True)
        self.cuisine.bash.addPath("/opt/jumpscale8/bin", action=True)

        if start:
            cmd=self.cuisine.bash.cmdGetPath("skydns")
            self.cuisine.systemd.ensure("skydns",cmd)        

    @actionrun(action=True)
    def caddy(self,ssl=False,start=True):
        self.GOPATH
        self.cuisine.golang.get("github.com/mholt/caddy",action=True)
        self.cuisine.file_copy(j.sal.fs.joinPaths(self.GOPATH, 'bin', 'caddy'),'/opt/jumpscale8/bin',action=True)
        self.cuisine.bash.addPath("/opt/jumpscale8/bin" ,action=True)

        self.cuisine.systemd.stop("caddy") #will also kill

        if ssl:
            PORTS=":443"
            self.cuisine.fw.allowIncoming(443)
            self.cuisine.fw.allowIncoming(80)

            if self.cuisine.process.tcpport_check(80,"") or self.cuisine.process.tcpport_check(443,""):
                raise RuntimeError("port 80 or 443 are occupied, cannot install caddy")

        else:
            if self.cuisine.process.tcpport_check(80,""):
                raise RuntimeError("port 80 is occupied, cannot install caddy")

            PORTS=":80"
            self.cuisine.fw.allowIncoming(80)
        C="""
        $ports
        gzip
        log /optvar/caddy/log/access.log
        errors {
            log /optvar/caddy/log/errors.log
        }
        root /optvar/caddy/www
        """
        C=C.replace("$ports",PORTS)
        cpath="/etc/caddy/caddyfile.conf"
        self.cuisine.dir_ensure("/etc/caddy")
        self.cuisine.file_write(cpath,C)
        self.cuisine.dir_ensure("/optvar/caddy/log/")
        self.cuisine.dir_ensure("/optvar/caddy/www/")

        if start:
            cmd=self.cuisine.bash.cmdGetPath("caddy")
            self.cuisine.systemd.ensure("caddy","%s -conf=\"%s\""%(cmd,cpath))        


    def caddyConfig(self,sectionname,config):
        """
        config format see https://caddyserver.com/docs/caddyfile
        """
        pass


    @actionrun(action=True)
    def etcd(self,start=True):
        C="""
        set -ex
        ORG_PATH="github.com/coreos"
        REPO_PATH="${ORG_PATH}/etcd"

        go get -x -d -u github.com/coreos/etcd

        cd $GOPATH/src/$REPO_PATH

        git checkout v2.2.2

        go get -d .


        CGO_ENABLED=0 go build -a -installsuffix cgo -ldflags "-s -X ${REPO_PATH}/version.GitSHA=v2.2.2" -o /opt/jumpscale8/bin/etcd .

        """
        C=self.cuisine.bash.replaceEnvironInText(C)
        self.cuisine.run_script(C,profile=True,action=True)
        self.cuisine.bash.addPath("/opt/jumpscale8/bin",action=True)

        if start:
            cmd=self.cuisine.bash.cmdGetPath("etcd")
            self.cuisine.systemd.ensure("etcd",cmd)


    def redis(self):
        C="""
        #!/bin/bash
        set -ex

        # groupadd -r redis && useradd -r -g redis redis

        mkdir -p /opt/redis
        cd /opt/redis
        wget http://download.redis.io/releases/redis-3.0.6.tar.gz
        tar xzf redis-3.0.6.tar.gz
        cd redis-3.0.6
        make

        # rm -rf /build/opt/redis
        # mkdir -p /build/opt/redis
        # rm -rf /build/optvar/redis/
        # mkdir -p /build/optvar/redis/

        rm -f /usr/local/bin/redis-server
        rm -f /usr/local/bin/redis-cli
        cp /opt/redis/redis-3.0.6/src/redis-server /opt/jumpscale8/bin/
        cp /opt/redis/redis-3.0.6/src/redis-cli /opt/jumpscale8/bin/

        mkdir -p /optvar/cfg/
        cp /bd_build/redis.conf /optvar/cfg/

        rm -rf /opt/redis

        """
        C=self.cuisine.bash.replaceEnvironInText(C)
        self.cuisine.run_script(C,profile=True)
        self.cuisine.bash.addPath("/opt/jumpscale8/bin",action=True)

    def vulcand(self):
        C='''
        #!/bin/bash
        set -e
        source /bd_build/buildconfig
        set -x

        export GOPATH=/tmp/vulcandgopath

        if [ ! -d $GOPATH ]; then
            mkdir -p $GOPATH
        fi

        go get -d github.com/vulcand/vulcand

        cd $GOPATH/src/github.com/vulcand/vulcand
        CGO_ENABLED=0 go build -a -ldflags '-s' -installsuffix nocgo .
        GOOS=linux go build -a -tags netgo -installsuffix cgo -ldflags '-w' -o ./vulcand .
        GOOS=linux go build -a -tags netgo -installsuffix cgo -ldflags '-w' -o ./vctl/vctl ./vctl
        GOOS=linux go build -a -tags netgo -installsuffix cgo -ldflags '-w' -o ./vbundle/vbundle ./vbundle

        mkdir -p /build/vulcand
        cp $GOPATH/src/github.com/vulcand/vulcand/vulcand /opt/jumpscale8/bin/
        cp $GOPATH/src/github.com/vulcand/vulcand/vctl/vctl /opt/jumpscale8/bin/
        cp $GOPATH/src/github.com/vulcand/vulcand/vbundle/vbundle /opt/jumpscale8/bin/

        rm -rf $GOPATH

        '''
        C=self.cuisine.bash.replaceEnvironInText(C)
        self.cuisine.run_script(C,profile=True)
        self.cuisine.bash.addPath("/opt/jumpscale8/bin",action=True)
