
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

    @actionrun(action=True)
    def skydns(self,start=True):
        self.cuisine.golang.install()
        self.cuisine.golang.get("github.com/skynetservices/skydns",action=True)
        self.cuisine.file_copy(self.cuisine.joinpaths('$goDir', 'bin', 'skydns'), '$binDir', action=True)
        self.cuisine.bash.addPath("$binDir", action=True)

        if start:
            cmd = self.cuisine.bash.cmdGetPath("skydns")
            self.cuisine.systemd.ensure("skydns", cmd)

    @actionrun(action=True)
    def caddy(self,ssl=False,start=True, dns=None):
        self.cuisine.golang.install()
        self.cuisine.golang.get("github.com/mholt/caddy",action=True)
        self.cuisine.file_copy(self.cuisine.joinpaths('$goDir', 'bin', 'caddy'), '$binDir', action=True)
        self.cuisine.bash.addPath("$binDir", action=True)

        if ssl and dns:
            addr = dns
        else:
            addr = ':80'

        C="""
        $addr
        gzip
        log $varDir/caddy/log/access.log
        errors {
            log $varDir/caddy/log/errors.log
        }
        root $varDir/caddy/www
        """
        C = C.replace("$addr", addr)
        cpath = "/etc/caddy/caddyfile.conf"
        self.cuisine.dir_ensure("/etc/caddy")
        self.cuisine.file_write(cpath, C)
        self.cuisine.dir_ensure("$varDir/caddy/log/")
        self.cuisine.dir_ensure("$varDir/caddy/www/")

        if start:
            self.cuisine.systemd.stop("caddy")  # will also kill
            if ssl:
                self.cuisine.fw.allowIncoming(443)
                self.cuisine.fw.allowIncoming(80)

                if self.cuisine.process.tcpport_check(80,"") or self.cuisine.process.tcpport_check(443,""):
                    raise RuntimeError("port 80 or 443 are occupied, cannot install caddy")

            else:
                if self.cuisine.process.tcpport_check(80,""):
                    raise RuntimeError("port 80 is occupied, cannot install caddy")

                PORTS=":80"
                self.cuisine.fw.allowIncoming(80)
            cmd = self.cuisine.bash.cmdGetPath("caddy")
            self.cuisine.systemd.ensure("caddy", '%s -conf="%s"' % (cmd, cpath))


    def caddyConfig(self,sectionname,config):
        """
        config format see https://caddyserver.com/docs/caddyfile
        """
        raise RuntimeError("needs to be implemented")
        pass

    @actionrun(action=True)
    def aydostore(self, addr='0.0.0.0:8090', backend="$varDir/aydostor", start=True):
        """
        Build and Install aydostore
        @input addr, address and port on which the service need to listen. e.g. : 0.0.0.0:8090
        @input backend, directory where to save the data push to the store
        """
        self.cuisine.golang.install()
        self.cuisine.golang.get("github.com/Jumpscale/aydostorex", action=True)
        self.cuisine.file_copy(self.cuisine.joinpaths(self.goDir, 'bin', 'aydostorex'), '$base/bin',action=True)
        self.cuisine.bash.addPath("$base/bin", action=True)

        self.cuisine.systemd.stop("aydostorex") # will also kill

        self.cuisine.dir_ensure("$cfgDir/aydostorex")
        self.cuisine.dir_ensure(backend)
        config = {
            'listen_addr': addr,
            'store_root': backend,
        }
        content = j.data.serializer.toml.dumps(config)
        self.cuisine.file_write("$cfgDir/aydostorex/config.toml", content)

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
            self.cuisine.systemd.ensure("aydostorex", '%s --config $cfgDir/aydostorex/config.toml' % cmd)


    @actionrun(action=True)
    def agentcontroller(self, start=True):
        """
        config: https://github.com/Jumpscale/agent2/wiki/agent-configuration
        """

        self.cuisine.golang.install()
        j.actions.setRunId("installAgentController")

        self.cuisine.pip.upgrade('pip')
        self.cuisine.pip.install('pytoml')
        self.cuisine.pip.install('pygo')
        self.cuisine.golang.install()
        self.syncthing()
        self.agent()
        self.agentcontroller_build()

        if start:
            self._startAgent()
            self._startAgentController()

    @actionrun(action=True)
    def syncthing(self):

        self.cuisine.golang.install()

        if not self.cuisine.isMac:
            # self.cuisine.golang.get("golint")

            goDir = self.cuisine.dir_paths['goDir']

            # self.cuisine.dir_ensure("$appDir/syncthing", recursive=True)
            # self.cuisine.dir_ensure("$binDir/syncthing", recursive=True)

            url = "https://github.com/syncthing/syncthing.git"
            sourcepath = self.cuisine.git.pullRepo(url, dest='%s/src/github.com/syncthing/syncthing' % goDir, ssh=False)
            self.cuisine.run('cd %s && godep restore' % sourcepath, profile=True)
            self.cuisine.file_unlink('%s/src/github.com/syncthing/syncthing/syncthing' % goDir)
            self.cuisine.dir_remove('%s/src/github.com/syncthing/syncthing/bin' % goDir)
            self.cuisine.run("cd %s && ./build.sh" % sourcepath, profile=True)

            self.cuisine.file_move("%s/bin/syncthing"%sourcepath, "$binDir/syncthing")
        else:
            #broken on mac?
            url="https://github.com/syncthing/syncthing/releases/download/v0.12.17/syncthing-macosx-amd64-v0.12.17.tar.gz"
            self.cuisine.file_download(url,"$tmpDir",overwrite=False,retry=3,timeout=0,expand=True)

            self.cuisine.file_copy("$tmpDir/syncthing-macosx-amd64-v0.12.17/syncthing","$binDir/syncthing")
            self.cuisine.run("rm -rf $tmpDir/syncthing*")

    @actionrun(action=True)
    def agent(self,start=True):
        self.syncthing()

        self.cuisine.tmux.killWindow("main","agent")

        self.cuisine.process.kill("agent8")

        self.cuisine.dir_ensure("$cfgDir/agent8", recursive=True)

        url = "github.com/Jumpscale/agent2"
        self.cuisine.golang.get(url)

        sourcepath = "$goDir/src/github.com/Jumpscale/agent2"

        self.cuisine.run("cd %s;go build ."%sourcepath,profile=True)

        self.cuisine.file_move("%s/agent2"%sourcepath, "$binDir/agent8")

        # link extensions
        self.cuisine.dir_remove("$cfgDir/agent8/extensions")
        self.cuisine.file_link("%s/extensions" % sourcepath, "$cfgDir/agent8/extensions")

        # manipulate config file
        C=self.cuisine.file_read("%s/agent.toml"%sourcepath)

        self.cuisine.file_write("$cfgDir/agent8/agent.toml", C, replaceArgs=True)
        self.cuisine.file_write("$cfgDir/agent8/agent.toml.org", C, replaceArgs=False)

        # self.cuisine.dir_ensure("$cfgDir/agent8/agent8/conf", recursive=True)

        if start:
            self._startAgent()

    @actionrun(action=True)
    def agentcontroller_build(self,start=False):

        self.cuisine.tmux.killWindow("main","ac")

        self.cuisine.process.kill("agentcontroller8")

        self.cuisine.dir_ensure("$cfgDir/agentcontroller8", recursive=True)

        url = "github.com/Jumpscale/agentcontroller2"
        self.cuisine.golang.get(url)
        sourcepath = "$goDir/src/github.com/Jumpscale/agentcontroller2"

        #do the actual building
        self.cuisine.run("cd %s;go build ."%sourcepath,profile=True)

        self.cuisine.file_move("%s/agentcontroller2"%sourcepath, "$binDir/agentcontroller8")

        C = self.cuisine.file_read("%s/agentcontroller.toml"%sourcepath)
        self.cuisine.file_write('$cfgDir/agentcontroller8/agentcontroller.toml', C)
        self.cuisine.file_write('$cfgDir/agentcontroller8/agentcontroller.toml.org', C, replaceArgs=False)

        self.cuisine.dir_remove("$cfgDir/agentcontroller8/extensions")
        self.cuisine.file_link("%s/extensions" % sourcepath, "$cfgDir/agentcontroller8/extensions")

        if start:
            self.agent()
            self._startAgent()
            self._startAgentController

    @actionrun(action=True)
    def _startAgent(self):
        appbase = self.cuisine.joinpaths(j.dirs.cfgDir, "agent8")
        cfgfile_agent = "$cfgDir/agent8/agent.toml"
        binPath = self.cuisine.joinpaths(self.cuisine.dir_paths['binDir'],'agent8')
        print("connection test ok to agentcontroller")
        #@todo (*1*) need to implement to work on node
        env={}
        env["TMPDIR"]=self.cuisine.dir_paths["tmpDir"]
        cmd = "%s -c %s" % (binPath, cfgfile_agent)
        self.cuisine.tmux.executeInScreen("main", screenname="agent", cmd=cmd, wait=0, cwd=appbase, env=env, user='root', tmuxuser=None)

    @actionrun(action=True)
    def _startAgentController(self):
        appbase = self.cuisine.joinpaths(j.dirs.cfgDir, "agentcontroller8")
        cfgfile_ac = self.cuisine.joinpaths(appbase, "agentcontroller.toml")
        binPath = self.cuisine.joinpaths(j.dirs.binPath, 'agentcontroller8')
        env = {}
        env["TMPDIR"] = self.cuisine.dir_paths["tmpDir"]
        cmd = "%s -c %s" % (binPath, cfgfile_ac)
        self.cuisine.tmux.executeInScreen("main", screenname="ac", cmd=cmd, wait=0, cwd=appbase, env=env, user='root', tmuxuser=None)

    @actionrun(action=True)
    def etcd(self,start=True):
        self.cuisine.golang.install()
        C="""
        set -ex
        ORG_PATH="github.com/coreos"
        REPO_PATH="${ORG_PATH}/etcd"

        go get -x -d -u github.com/coreos/etcd

        cd $goDir/src/$REPO_PATH

        git checkout v2.2.2

        go get -d .


        CGO_ENABLED=0 go build -a -installsuffix cgo -ldflags "-s -X ${REPO_PATH}/version.GitSHA=v2.2.2" -o $binDir/etcd .

        """
        C=self.cuisine.bash.replaceEnvironInText(C)
        self.cuisine.run_script(C,profile=True,action=True)
        self.cuisine.bash.addPath("$base/bin",action=True)

        if start:
            self.cuisine.process.kill("etcd")
            self.cuisine.systemd.ensure("etcd","etcd")

    @actionrun(action=True)
    def redis(self,name="main",ip="localhost", port=6379, maxram=200, appendonly=True,snapshot=False,slave=(),ismaster=False,passwd=None,unixsocket=True,start=True):
        self.cuisine.installer.base()
        if not self.cuisine.isMac:

            C="""
            #!/bin/bash
            set -ex

            # groupadd -r redis && useradd -r -g redis redis

            mkdir -p $tmpDir/build/redis
            cd $tmpDir/build/redis
            wget http://download.redis.io/releases/redis-3.0.6.tar.gz
            tar xzf redis-3.0.6.tar.gz
            cd redis-3.0.6
            make

            rm -f /usr/local/bin/redis-server
            rm -f /usr/local/bin/redis-cli

            """
            C=self.cuisine.bash.replaceEnvironInText(C)
            C=self.cuisine.args_replace(C)
            self.cuisine.run_script(C,profile=True,action=True)
            #move action
            C="""
            set -ex
            mkdir -p $base/bin/
            cp $tmpDir/build/redis/redis-3.0.6/src/redis-server $base/bin/
            cp $tmpDir/build/redis/redis-3.0.6/src/redis-cli $base/bin/

            rm -rf $base/apps/redis
            """
            C=self.cuisine.bash.replaceEnvironInText(C)
            C=self.cuisine.args_replace(C)
            self.cuisine.run_script(C,profile=True,action=True)
        else:
            if self.cuisine.command_check("redis-server")==False:
                self.cuisine.package.install("redis")
            cmd=self.cuisine.command_location("redis-server")
            dest="%s/redis-server"%self.cuisine.dir_paths["binDir"]
            if cmd!=dest:
                self.cuisine.file_copy(cmd,dest)

        self.cuisine.bash.addPath("%s/bin"%self.cuisine.dir_paths["base"],action=True)

        j.clients.redis.executor=self.executor
        j.clients.redis.cuisine=self.cuisine
        j.clients.redis.configureInstance(name, ip, port, maxram=maxram, appendonly=appendonly, \
            snapshot=snapshot, slave=slave, ismaster=ismaster, passwd=passwd, unixsocket=True)
        dpath,cpath=j.clients.redis._getPaths(name)

        if start:
            cmd = "%s %s" % (self.cuisine.command_location("redis-server"), cpath)
            self.cuisine.systemd.ensure(name="redis_%s"%name,cmd=cmd,env={}, path='$binDir')

    @actionrun(action=True)
    def mongodb(self, start=True):
        self.cuisine.installer.base()
        exists=self.cuisine.command_check("mongod")

        if exists:
            cmd=self.cuisine.command_location("mongod")
            dest="%s/mongod"%self.cuisine.dir_paths["binDir"]
            if cmd!=dest:
                self.cuisine.file_copy(cmd,dest)

        else:

            appbase = self.cuisine.dir_paths("binDir")

            url=None
            if self.cuisine.isUbuntu:
                url = 'https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu1404-3.2.1.tgz'
            elif self.cuisine.isArch:
                self.cuisine.package.install("mongodb")
            elif self.cuisine.isMac: #@todo better platform mgmt
                url = 'https://fastdl.mongodb.org/osx/mongodb-osx-x86_64-3.2.1.tgz'
            else:
                raise RuntimeError("unsupported platform")
                return

            if url!=None:
                self.cuisine.file_download(url, to="$tmpDir",overwrite=False,expand=True)
                tarpath = self.cuisine.fs_find("$tmpDir",recursive=True,pattern="*mongodb*.tgz",type='f')[0]
                self.cuisine.file_expand(tarpath,"$tmpDir")
                extracted = self.cuisine.fs_find("$tmpDir",recursive=True,pattern="*mongodb*",type='d')[0]
                for file in self.cuisine.fs_find('%s/bin/' %extracted,type='f'):
                    self.cuisine.file_copy(file,appbase)

        self.cuisine.dir_ensure('$varDir/data/db')

        if start:
            cmd="mongod --dbpath $varDir/data/db"
            c.cuisine.process.kill("mongod")
            self.cuisine.systemd.ensure("mongod",cmd=cmd,env={},path="")

    def influxdb(self, start=True):
        self.cuisine.installer.base()

        if self.cuisine.isMac:
            self.cuisine.package.mdupdate()
            self.cuisine.package.install('influxdb')
        if self.cuisine.isUbuntu:
            self.cuisine.dir_ensure("$cfgDir/influxdb")
            C= """
cd $tmpDir
wget https://s3.amazonaws.com/influxdb/influxdb-0.10.0-1_linux_amd64.tar.gz
tar xvfz influxdb-0.10.0-1_linux_amd64.tar.gz
cp influxdb-0.10.0-1/usr/bin/influxd $binDir
cp influxdb-0.10.0-1/etc/influxdb/influxdb.conf $cfgDir/influxdb
cp influxdb-0.10.0-1/etc/influxdb/influxdb.conf $cfgDir/influxdb/influxdb.conf.org"""
            C = self.cuisine.bash.replaceEnvironInText(C)
            C = self.cuisine.args_replace(C)
            self.cuisine.run_script(C, profile=True, action=True)
            self.cuisine.bash.addPath("$binDir", action=True)

        if start:
            binPath = c.bash.cmdGetPath('influxd')
            cmd = "%s -config $cfgDir/influxdb/influxdb.conf" % (binPath)
            c.cuisine.process.kill("influxdb")
            self.cuisine.systemd.ensure("influxdb", cmd=cmd, env={}, path="")

    @actionrun(action=True)
    def vulcand(self):
        C='''
        #!/bin/bash
        set -e
        source /bd_build/buildconfig
        set -x

        export goDir=$tmpDir/vulcandgoDir

        if [ ! -d $goDir ]; then
            mkdir -p $goDir
        fi

        go get -d github.com/vulcand/vulcand

        cd $goDir/src/github.com/vulcand/vulcand
        CGO_ENABLED=0 go build -a -ldflags '-s' -installsuffix nocgo .
        GOOS=linux go build -a -tags netgo -installsuffix cgo -ldflags '-w' -o ./vulcand .
        GOOS=linux go build -a -tags netgo -installsuffix cgo -ldflags '-w' -o ./vctl/vctl ./vctl
        GOOS=linux go build -a -tags netgo -installsuffix cgo -ldflags '-w' -o ./vbundle/vbundle ./vbundle

        mkdir -p /build/vulcand
        cp $goDir/src/github.com/vulcand/vulcand/vulcand $base/bin/
        cp $goDir/src/github.com/vulcand/vulcand/vctl/vctl $base/bin/
        cp $goDir/src/github.com/vulcand/vulcand/vbundle/vbundle $base/bin/

        rm -rf $goDir

        '''
        C=self.cuisine.bash.replaceEnvironInText(C)
        self.cuisine.run_script(C,profile=True)
        self.cuisine.bash.addPath("$base/bin",action=True)
