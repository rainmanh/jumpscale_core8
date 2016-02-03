
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


    @actionrun(action=True)
    def skydns(self,start=True):
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
    def aydostore(self, addr='0.0.0.0:8090', backend="/tmp/aydostor", start=True):
        """
        Build and Install aydostore
        @input addr, address and port on which the service need to listen. e.g. : 0.0.0.0:8090
        @input backend, directory where to save the data push to the store
        """
        self.GOPATH
        self.cuisine.golang.get("github.com/Jumpscale/aydostorex", action=True)
        self.cuisine.file_copy(j.sal.fs.joinPaths(self.GOPATH, 'bin', 'aydostorex'), '/opt/jumpscale8/bin',action=True)
        self.cuisine.bash.addPath("/opt/jumpscale8/bin", action=True)

        self.cuisine.systemd.stop("aydostorex") # will also kill

        self.cuisine.dir_ensure("/etc/aydostorex")
        self.cuisine.dir_ensure(backend)
        config = {
            'listen_addr': addr,
            'store_root': backend,
        }
        content = j.data.serializer.toml.dumps(config)
        self.cuisine.file_write("/etc/aydostorex/config.toml", content)

        res = addr.split(":")
        if len(res) == 2:
            addr, port = res[0], res[1]
        else:
            addr, port = res[0], '8090'

        self.cuisine.fw.allowIncoming(port)
        if self.cuisine.process.tcpport_check(port,""):
            raise RuntimeError("port %d is occupied, cannot start aydostorex" % port)

        if start:
            cmd = self.cuisine.bash.cmdGetPath("aydostorex")
            self.cuisine.systemd.ensure("aydostorex", '%s --config /etc/aydostorex/config.toml' % cmd)

    @actionrun(action=True)
    def agentcontroller(self, start=True):
        """
        config: https://github.com/Jumpscale/agent2/wiki/agent-configuration
        """
        j.actions.setRunId("installAgentController")

        self.cuisine.pip.upgrade('pip')
        self.cuisine.pip.install('pytoml')
        self.cuisine.pip.install('pygo')
        self.cuisine.golang.install()
        self.syncthing()
        self.agent()
        self.agentcontroller()

        if start:
            self._startAgent()
            self._startAgentController()

    @actionrun(action=True)
    def syncthing(self):
        appbase = j.sal.fs.joinPaths(j.dirs.base, "apps", "syncthing")
        GOPATH = self.cuisine.bash.environGet('GOPATH')

        url = "git@github.com:syncthing/syncthing.git"
        dest = self.cuisine.git.pullRepo(url, dest='%s/src/github.com/syncthing/syncthing' % GOPATH)
        self.cuisine.run('cd %s && godep restore' % dest, profile=True)
        self.cuisine.run("cd %s && ./build.sh noupgrade" % dest, profile=True)
        self.cuisine.dir_ensure(appbase, recursive=True)
        self.cuisine.file_copy(j.sal.fs.joinPaths(dest, 'syncthing'), j.sal.fs.joinPaths(GOPATH, 'bin'), recursive=True)
        self.cuisine.file_copy(j.sal.fs.joinPaths(GOPATH, 'bin', 'syncthing'), appbase, recursive=True)

    @actionrun(action=True)
    def agent(self):
        GOPATH = self.cuisine.bash.environGet('GOPATH')
        appbase = j.sal.fs.joinPaths(j.dirs.base, "apps", "agent8")
        self.cuisine.dir_ensure(appbase, recursive=True)

        url = "github.com/Jumpscale/agent2"
        self.cuisine.golang.get(url)
        dest = j.sal.fs.joinPaths(GOPATH, 'src/github.com/Jumpscale/agent2')

        agent2_dest = j.sal.fs.joinPaths(appbase, "agent8")
        syncthing_dest = j.sal.fs.joinPaths(appbase, "syncthing")
        self.cuisine.file_copy(j.sal.fs.joinPaths(GOPATH, 'bin', "agent2"), agent2_dest)
        self.cuisine.file_copy(j.sal.fs.joinPaths(GOPATH, 'bin', "syncthing"), syncthing_dest)

        # link extensions
        extdir = j.sal.fs.joinPaths(appbase, "extensions")
        self.cuisine.dir_remove(extdir)
        self.cuisine.file_link("%s/extensions" % dest, extdir)

        # manipulate config file
        cfgfile = '%s/agent.toml' % appbase
        self.cuisine.file_copy("%s/agent.toml" % dest, cfgfile)

        self.cuisine.file_copy("%s/conf" % dest, j.sal.fs.joinPaths(appbase, "conf"), recursive=True )

    @actionrun(action=True)
    def agentcontroller(self):
        GOPATH = self.cuisine.bash.environGet('GOPATH')
        appbase = j.sal.fs.joinPaths(j.dirs.base, "apps", "agentcontroller8")
        self.cuisine.dir_ensure(appbase, recursive=True)

        url = "github.com/Jumpscale/agentcontroller2"
        self.cuisine.golang.get(url)
        dest = j.sal.fs.joinPaths(GOPATH, 'src/github.com/Jumpscale/agentcontroller2')

        destfile = j.sal.fs.joinPaths(appbase, "agentcontroller8")
        self.cuisine.file_copy(j.sal.fs.joinPaths(GOPATH, 'bin', "agentcontroller2"), destfile)

        cfgfile = '%s/agentcontroller.toml' % appbase
        self.cuisine.file_copy("%s/agentcontroller.toml" % dest, cfgfile)

        extdir = j.sal.fs.joinPaths(appbase, "extensions")
        self.cuisine.dir_remove(extdir)
        self.cuisine.dir_ensure(extdir)
        self.cuisine.dir_file_link("%s/extensions" % dest, extdir)

        cfg = j.data.serializer.toml.loads(self.cuisine.file_read(cfgfile))
        cfg['jumpscripts']['python_path'] = "%s:%s" % (extdir, j.dirs.jsLibDir)
        content = j.data.serializer.toml.dumps(cfg)
        self.cuisine.file_write(cfgfile, content)

    @actionrun(action=True)
    def _startAgent(self):
        appbase = j.sal.fs.joinPaths(j.dirs.base, "apps", "agent8")
        cfgfile_agent = j.sal.fs.joinPaths(appbase, "agent.toml")
        j.sal.nettools.waitConnectionTest("127.0.0.1", 8966, timeout=2)
        print("connection test ok to agentcontroller")
        self.cuisine.tmux.executeInScreen("main", screenname="agent", cmd="./agent8 -c %s" % cfgfile_agent, wait=0, cwd=appbase, env=None, user='root', tmuxuser=None)

    @actionrun(action=True)
    def _startAgentController(self):
        appbase = j.sal.fs.joinPaths(j.dirs.base, "apps", "agentcontroller8")
        cfgfile_ac = j.sal.fs.joinPaths(appbase, "agentcontroller.toml")
        self.cuisine.tmux.executeInScreen("main", screenname="ac", cmd="./agentcontroller8 -c %s" % cfgfile_ac, wait=0, cwd=appbase, env=None, user='root', tmuxuser=None)


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

    @actionrun(action=True)
    def redis(self,start=True):

        self.cuisine.systemd.stop("redis-server")
        self.cuisine.systemd.stop("redis")

        C="""
        #!/bin/bash
        set -ex

        # groupadd -r redis && useradd -r -g redis redis

        mkdir -p /tmp/build/redis
        cd /tmp/build/redis
        wget http://download.redis.io/releases/redis-3.0.6.tar.gz
        tar xzf redis-3.0.6.tar.gz
        cd redis-3.0.6
        make

        rm -f /usr/local/bin/redis-server
        rm -f /usr/local/bin/redis-cli

        """
        C=self.cuisine.bash.replaceEnvironInText(C)
        self.cuisine.run_script(C,profile=True,action=True)
        #move action
        C="""
        set -ex
        cp /tmp/build/redis/redis-3.0.6/src/redis-server /opt/jumpscale8/bin/
        cp /tmp/build/redis/redis-3.0.6/src/redis-cli /opt/jumpscale8/bin/

        rm -rf /opt/redis
        mkdir -p /optvar/cfg/
        cp /tmp/build/redis/redis-3.0.6/redis.conf /optvar/cfg/
        """
        self.cuisine.run_script(C,profile=True,action=True)
        self.cuisine.bash.addPath("/opt/jumpscale8/bin",action=True)

        if start:
            cmd=self.cuisine.bash.cmdGetPath("redis-server")
            self.cuisine.systemd.ensure("redis","/%s /optvar/cfg/redis.conf"%(cmd))    

    def all(self):
        self.cuisine.installerdevelop.pip()
        self.cuisine.installerdevelop.python()
        self.cuisine.installerdevelop.jumpscale8()
        self.redis(start=False)
        self.etcd(start=False)
        self.caddy(start=False)
        self.skydns(start=False)


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
