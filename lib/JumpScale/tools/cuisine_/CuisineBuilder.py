
from JumpScale import j


from ActionDecorator import ActionDecorator
from CuisineMongoCluster import mongoCluster


class actionrun(ActionDecorator):
    def __init__(self, *args, **kwargs):
        ActionDecorator.__init__(self, *args, **kwargs)
        self.selfobjCode = "cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.builder"


class CuisineBuilder(object):

    def __init__(self,executor,cuisine):
        self.executor=executor
        self.cuisine=cuisine
        self.bash=self.cuisine.bash
        self.mongoCluster = mongoCluster

    def all(self,start=False, sandbox=False, aydostor=None):
        self.cuisine.installerdevelop.pip()
        self.cuisine.installerdevelop.python()
        self.cuisine.installerdevelop.jumpscale8()
        self.redis(start=start, force=True)
        # self.agentcontroller(start=start)
        self.etcd(start=start)
        self.caddy(start=start)
        self.skydns(start=start)
        self.influxdb(start=start)
        self.weave(start=start)
        self.mongodb(start=start)
        self.cuisine.portal.install(start=start)
        if sandbox:
            self.sandbox(aydostor)

    def sandbox(self, aydostor, python=True):
        """
        aydostor : addr to the store you want to populate. e.g.: https://stor.jumpscale.org/storx
        python : do you want to sandbox python too ? if you have segfault after trying sandboxing python, re run with python=False
        """
        # jspython is generated during install,need to copy it back into /opt before sandboxing
        self.cuisine.file_copy('/usr/local/bin/jspython', '/opt/jumpscale8/bin')
        cmd = "j.tools.cuisine.local.builder.dedupe(['/opt'], 'js8_opt', '%s', sandbox_python=%s)" % (aydostor, python)
        self.cuisine.run('js "%s"' % cmd)
        url_opt = '%s/static/js8_opt' % aydostor

        cmd = "j.tools.cuisine.local.builder.dedupe(['/optvar'], 'js8_optvar', '%s', sandbox_python=%s)" % (aydostor, False)
        self.cuisine.run('js "%s"' % cmd)
        url_optvar = '%s/static/js8_optvar' % aydostor

        return (url_opt, url_optvar)

    def _sandbox_python(self, python=True):
        print("START SANDBOX")
        if python:
            paths = []
            paths.append("/usr/lib/python3.5/")
            paths.append("/usr/local/lib/python3.5/dist-packages")
            paths.append("/usr/lib/python3/dist-packages")

            excludeFileRegex=["-tk/","/lib2to3","-34m-",".egg-info"]
            excludeDirRegex=["/JumpScale","\.dist-info","config-x86_64-linux-gnu","pygtk"]

            dest = j.sal.fs.joinPaths(self.cuisine.dir_paths['base'], 'lib')

            for path in paths:
                j.tools.sandboxer.copyTo(path, dest, excludeFileRegex=excludeFileRegex, excludeDirRegex=excludeDirRegex)

            if not j.do.exists("%s/bin/python" % self.cuisine.dir_paths['base']):
                j.do.copyFile("/usr/bin/python3.5", "%s/bin/python" % self.cuisine.dir_paths['base'])

        j.tools.sandboxer.sandboxLibs("%s/lib" % self.cuisine.dir_paths['base'], recursive=True)
        j.tools.sandboxer.sandboxLibs("%s/bin" % self.cuisine.dir_paths['base'], recursive=True)
        print("SANDBOXING DONE, ALL OK IF TILL HERE, A Segfault can happen because we have overwritten ourselves.")

    def dedupe(self, dedupe_path, namespace, store_addr, output_dir='/tmp/sandboxer', sandbox_python=True):
        self.cuisine.dir_remove(output_dir)

        if sandbox_python:
            self._sandbox_python()

        if not j.data.types.list.check(dedupe_path):
            dedupe_path = [dedupe_path]

        for path in dedupe_path:
            print("DEDUPE:%s" % path)
            j.tools.sandboxer.dedupe(path, storpath=output_dir, name=namespace, reset=False, append=True)

        store_client = j.clients.storx.get(store_addr)
        files_path = j.sal.fs.joinPaths(output_dir, 'files')
        files = j.sal.fs.listFilesInDir(files_path, recursive=True)
        error_files = []
        for f in files:
            src_hash = j.data.hash.md5(f)
            print('uploading %s' % f)
            uploaded_hash = store_client.putFile(namespace, f)
            if src_hash != uploaded_hash:
                error_files.append(f)
                print("%s hash doesn't match\nsrc     :%32s\nuploaded:%32s" % (f, src_hash, uploaded_hash))

        if len(error_files) == 0:
            print("all uploaded ok")
        else:
            raise RuntimeError('some files didnt upload properly. %s' % ("\n".join(error_files)))

        metadataPath = j.sal.fs.joinPaths(output_dir, "md", "%s.flist" % namespace)
        print('uploading %s' % metadataPath)
        store_client.putStaticFile(namespace+".flist", metadataPath)

    @actionrun(action=True)
    def skydns(self,start=True):
        self.cuisine.golang.install()
        self.cuisine.golang.get("github.com/skynetservices/skydns",action=True)
        self.cuisine.file_copy(self.cuisine.joinpaths('$goDir', 'bin', 'skydns'), '$binDir', action=True)
        self.cuisine.bash.addPath(self.cuisine.args_replace("$binDir"), action=True)

        if start:
            cmd=self.cuisine.bash.cmdGetPath("skydns")
            self.cuisine.processmanager.ensure("skydns",cmd + " -addr 0.0.0.0:53")

    @actionrun(action=True)
    def caddy(self,ssl=False,start=True, dns=None):
        self.cuisine.golang.install()
        self.cuisine.golang.get("github.com/mholt/caddy",action=True)
        self.cuisine.file_copy(self.cuisine.joinpaths('$goDir', 'bin', 'caddy'), '$binDir', action=True)
        self.cuisine.bash.addPath(self.cuisine.args_replace("$binDir"), action=True)

        if ssl and dns:
            addr = dns
        else:
            addr = ':80'

        C="""
        $addr
        gzip
        log $cfgDir/caddy/log/access.log
        errors {
            log $cfgDir/caddy/log/errors.log
        }
        root $cfgDir/caddy/www
        """
        C = C.replace("$addr", addr)
        C = self.cuisine.args_replace(C)
        cpath = self.cuisine.args_replace("$cfgDir/caddy/caddyfile.conf")
        self.cuisine.dir_ensure("$cfgDir/caddy")
        self.cuisine.dir_ensure("$cfgDir/caddy/log/")
        self.cuisine.dir_ensure("$cfgDir/caddy/www/")
        self.cuisine.file_write(cpath, C)

        if start:
            self.cuisine.processmanager.stop("caddy")  # will also kill
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
            self.cuisine.processmanager.ensure("caddy", '%s -conf=%s -email=info@greenitglobe.com' % (cmd, cpath))

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
        self.cuisine.file_copy(self.cuisine.joinpaths(self.cuisine.dir_paths['goDir'], 'bin', 'aydostorex'), '$base/bin',action=True)
        self.cuisine.bash.addPath("$base/bin", action=True)

        self.cuisine.processmanager.stop("aydostorex") # will also kill

        self.cuisine.dir_ensure("$cfgDir/aydostorex")
        backend = self.cuisine.args_replace(backend)
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
            self.cuisine.processmanager.ensure("aydostorex", '%s --config /etc/aydostorex/config.toml' % cmd)

    @actionrun(action=True)
    def installdeps(self):
        self.cuisine.installer.base()
        self.cuisine.golang.install()
        self.cuisine.pip.upgrade('pip')
        self.cuisine.pip.install('pytoml')
        self.cuisine.pip.install('pygo')
        self.cuisine.golang.install()

    @actionrun(action=True)
    def syncthing(self, start=True):
        """
        build and setup syncthing to run on :8384 , this can be changed from the config file in home  
        """
        self.installdeps()
        url = "git@github.com:syncthing/syncthing.git"

        self.cuisine.dir_remove('$goDir/src/github.com/syncthing/syncthing')
        dest = self.cuisine.git.pullRepo(url, branch="v0.11.25",  dest='$goDir/src/github.com/syncthing/syncthing')
        self.cuisine.run('cd %s && godep restore' % dest, profile=True)
        self.cuisine.run("cd %s && ./build.sh noupgrade" % dest, profile=True)
        self.cuisine.file_copy(self.cuisine.joinpaths(dest, 'syncthing'), "$goDir/bin/", recursive=True)
        self.cuisine.file_copy("$goDir/bin/syncthing", "$binDir", recursive=True)

        if start:
            self._startSyncthing()

    @actionrun(action=True)
    def agent(self,start=True, gid=None, nid=None):
        """
        builds and setsup dependencies of agent to run with the given gid and nid 
        niether can be zero 
        """

        self.installdeps()
        #self.cuisine.installer.jumpscale8()
        self.redis()
        self.mongodb()
        self.syncthing()

        self.cuisine.tmux.killWindow("main","agent")

        self.cuisine.process.kill("agent8")

        self.cuisine.dir_ensure("$cfgDir/agent8", recursive=True)
        self.cuisine.dir_ensure("$cfgDir/agent8/conf", recursive=True)
        self.cuisine.dir_ensure("$cfgDir/agent8/mid", recursive=True)

        url = "github.com/Jumpscale/agent8"
        self.cuisine.golang.get(url)

        sourcepath = "$goDir/src/github.com/Jumpscale/agent8"

        self.cuisine.run("cd %s && go build ." % sourcepath, profile=True)

        self.cuisine.file_move("%s/agent8" % sourcepath, "$binDir/agent8")

        # copy extensions
        self.cuisine.dir_remove("$cfgDir/agent8/extensions")
        self.cuisine.file_copy("%s/extensions" % sourcepath, "$cfgDir/agent8", recursive=True)
        self.cuisine.dir_ensure("$cfgDir/agent8/extensions/syncthing")
        self.cuisine.file_copy("$binDir/syncthing", "$cfgDir/agent8/extensions/syncthing/")

        # manipulate config file
        C = self.cuisine.file_read("%s/agent.toml" % sourcepath)
        cfg = j.data.serializer.toml.loads(C)
        cfg["main"]["message_ID_file"] = cfg["main"]["message_ID_file"].replace("./", "$cfgDir/agent8/")
        cfg["main"]["history_file"] = cfg["main"]["history_file"].replace("./", "$cfgDir/agent8/")
        cfg["main"]["include"] = cfg["main"]["include"].replace("./", "$cfgDir/agent8/")
        cfg["extensions"]["sync"]["cwd"] = cfg["extensions"]["sync"]["cwd"].replace("./", "$cfgDir/agent8/")
        cfg["extensions"]["jumpscript"]["cwd"] = cfg["extensions"]["jumpscript"]["cwd"].replace("./", "$cfgDir/agent8/")
        cfg["extensions"]["jumpscript_content"]["cwd"] = cfg["extensions"]["jumpscript_content"]["cwd"].replace("./", "$cfgDir/agent8/")
        cfg["extensions"]["js_daemon"]["cwd"] = cfg["extensions"]["js_daemon"]["cwd"].replace("./", "$cfgDir/agent8/")
        cfg["logging"]["db"]["address"] = cfg["logging"]["db"]["address"].replace("./", "$cfgDir/agent8/")
        C = j.data.serializer.toml.dumps(cfg)

        self.cuisine.file_write("$cfgDir/agent8/agent.toml", C, replaceArgs=True)
        self.cuisine.file_write("$cfgDir/agent8/agent.toml.org", C, replaceArgs=False)

        # self.cuisine.dir_ensure("$cfgDir/agent8/agent8/conf", recursive=True)

        if start:
            self._startMongodb()
            self._startRedis()
            self._startSyncthing()
            self._startAgent(nid, gid)

    @actionrun(action=True)
    def agentcontroller(self, start=True):
        """
        config: https://github.com/Jumpscale/agentcontroller8/
        """
        import re
        import hashlib
        self.installdeps()
        self.redis()
        self.mongodb()
        self.syncthing()
        
        self.cuisine.processmanager.remove("agentcontroller8")
        pm = self.cuisine.processmanager.get("tmux")
        pm.stop("syncthing")

        self.cuisine.dir_ensure("$cfgDir/agentcontroller8", recursive=True)

        #get repo 
        url = "github.com/Jumpscale/agentcontroller8"
        self.cuisine.golang.godep(url)
        sourcepath = "$goDir/src/github.com/Jumpscale/agentcontroller8"

        #do the actual building
        self.cuisine.run("cd %s && go build ." % sourcepath, profile=True)

        #move binary 
        self.cuisine.file_move("%s/agentcontroller8" % sourcepath, "$binDir/agentcontroller8")
        #edit config 
        C = self.cuisine.file_read("%s/agentcontroller.toml"%sourcepath)
        cfg = j.data.serializer.toml.loads(C)

        cfg["events"]["python_path"] = cfg["events"]["python_path"].replace("./", "$cfgDir/agentcontroller8/")
        cfg["processor"]["python_path"] = cfg["processor"]["python_path"].replace("./", "$cfgDir/agentcontroller8/")
        cfg["jumpscripts"]["python_path"] = cfg["jumpscripts"]["python_path"].replace("./", "$cfgDir/agentcontroller8/")
        cfg["jumpscripts"]["settings"]["jumpscripts_path"] = cfg["jumpscripts"]["settings"]["jumpscripts_path"].replace("./", "$cfgDir/agentcontroller8/")

        C = j.data.serializer.toml.dumps(cfg)
        self.cuisine.file_write('$cfgDir/agentcontroller8/agentcontroller.toml', C, replaceArgs=True)
        self.cuisine.file_write('$cfgDir/agentcontroller8/agentcontroller.toml.org', C, replaceArgs=False)

        #expose syncthing and get api key  
        sync_cfg = self.cuisine.file_read("$homeDir/.config/syncthing/config.xml")
        sync_conn = re.search(r'<address>([0-9.]+):([0-9]+)</', sync_cfg)
        apikey = re.search(r'<apikey>([\w\-]+)</apikey>', sync_cfg).group(1)
        sync_cfg = sync_cfg.replace(sync_conn.group(1), "0.0.0.0")
        sync_cfg = sync_cfg.replace(sync_conn.group(2), "18384")
        self.cuisine.file_write("$homeDir/.config/syncthing/config.xml", sync_cfg)


        #add jumpscripts file 
        self._startSyncthing()
        addr = "localhost"
        if not self.cuisine.executor.type == 'local':
            addr = self.executor.addr
        synccl = j.clients.syncthing.get(addr,18384, apikey=apikey)
        jumpscripts_path = self.cuisine.args_replace("$cfgDir/agentcontroller8/jumpscripts")
        jumpscripts_id = "jumpscripts-%s" % hashlib.md5(synccl.id_get().encode()).hexdigest()
        synccl.config_add_folder(jumpscripts_id, jumpscripts_path)


        #file copy 
        self.cuisine.dir_remove("$cfgDir/agentcontroller8/extensions")
        self.cuisine.file_copy("%s/extensions" % sourcepath, "$cfgDir/agentcontroller8/extensions", recursive=True)

        if start:
            self._startMongodb()
            self._startRedis()
            self._startSyncthing()
            self._startAgentController()


    def _startSyncthing(self):
        GOPATH = self.cuisine.bash.environGet('GOPATH')
        env={}
        env["TMPDIR"]=self.cuisine.dir_paths["tmpDir"]
        pm = self.cuisine.processmanager.get("tmux")
        pm.ensure(name="syncthing", cmd="./syncthing", path=self.cuisine.joinpaths(GOPATH, "bin"))


    def _startAgent(self, nid, gid):

        print("connection test ok to agentcontroller")
        #@todo (*1*) need to implement to work on node
        env={}
        env["TMPDIR"]=self.cuisine.dir_paths["tmpDir"]
        cmd = "$binDir/agent8 -nid %s -gid %s -c $cfgDir/agent8/agent.toml" % (nid, gid)
        pm = self.cuisine.processmanager.get("tmux")
        pm.ensure("agent8", cmd=cmd, path="$cfgDir/agent8",  env=env)

    def _startAgentController(self):
        env = {}
        env["TMPDIR"] = self.cuisine.dir_paths["tmpDir"]
        cmd = "$binDir/agentcontroller8 -c $cfgDir/agentcontroller8/agentcontroller.toml"
        pm = self.cuisine.processmanager.get("tmux")
        pm.ensure("agentcontroller8", cmd=cmd, path="$cfgDir/agentcontroller8/", env=env)

    def _startRedis(self):
        cmd="redis-server %s"%cpath
        self.cuisine.processmanager.ensure(name="redis_%s"%name,cmd=cmd,env={},path='$binDir')

    def _startMongodb(self):
        which = self.cuisine.command_location("mongod")
        cmd="%s --dbpath $varDir/data/db" % which
        self.cuisine.process.kill("mongod")
        self.cuisine.processmanager.ensure("mongod",cmd=cmd,env={},path="")

    @actionrun(action=True)
    def etcd(self,start=True, host=None, peers=[]):
        """
        Build and start etcd

        @start, bool start etcd after buildinf or not
        @host, string. host of this node in the cluster e.g: http://etcd1.com
        @peer, list of string, list of all node in the cluster. [http://etcd1.com, http://etcd2.com, http://etcd3.com]
        """
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
            if cmd and peers:
                cmd = self._etcd_cluster_cmd(host, peers)
            else:
                cmd = 'etcd'
            self.cuisine.processmanager.ensure("etcd", cmd)

    def _etcd_cluster_cmd(host, peers=[]):
        """
        return the command to execute to launch etcd as a static cluster
        @host, string. host of this node in the cluster e.g: http://etcd1.com
        @peer, list of string, list of all node in the cluster. [http://etcd1.com, http://etcd2.com, http://etcd3.com]
        """
        if host not in peers:
            peers.append(host)

        cluster = ""
        number = None
        for i, peer in enumerate(peers):
            cluster += 'infra{i}={host}:2380,'.format(i=i, host=peer)
            if peer == host:
                number = i
        cluster = cluster.rstrip(",")

        host = host.lstrip("http://").lstrip('https://')
        cmd = """
    etcd -name infra{i} -initial-advertise-peer-urls http://{host}:2380 \
      -listen-peer-urls http://{host}:2380 \
      -listen-client-urls http://{host}:2379,http://127.0.0.1:2379,http://{host}:4001,http://127.0.0.1:4001 \
      -advertise-client-urls http://{host}:2379,http://{host}:4001 \
      -initial-cluster-token etcd-cluster-1 \
      -initial-cluster {cluster} \
      -initial-cluster-state new
    """.format(host=host, cluster=cluster, i=number)
        return cmd

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
            self.cuisine.run_script(C,profile=True)
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
            self.cuisine.run_script(C,profile=True)
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
            self._startRedis()

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

            appbase = self.cuisine.dir_paths["binDir"]

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
            self._startMongodb()

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
            self.cuisine.bash.addPath(self.cuisine.args_replace("$binDir"), action=True)

        if start:
            binPath = self.cuisine.bash.cmdGetPath('influxd')
            cmd = "%s -config $cfgDir/influxdb/influxdb.conf" % (binPath)
            self.cuisine.process.kill("influxdb")
            self.cuisine.processmanager.ensure("influxdb", cmd=cmd, env={}, path="")

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

    @actionrun(action=True)
    def weave(self, start=True, peer=None, jumpscalePath=True):
        if jumpscalePath:
            binPath = self.cuisine.joinpaths(self.cuisine.dir_paths['binDir'], 'weave')
        else:
            binPath = '/usr/local/bin/weave'
        self.cuisine.dir_ensure(j.sal.fs.getParent(binPath))

        C = '''
        curl -L git.io/weave -o {binPath} && sudo chmod a+x {binPath}
        '''.format(binPath=binPath)
        C = self.cuisine.args_replace(C)
        self.cuisine.package.ensure('curl')
        self.cuisine.run_script(C, profile=True)
        self.cuisine.bash.addPath(j.sal.fs.getParent(binPath), action=True)

        if start:
            rc, out = self.cuisine.run("weave status", profile=True, die=False, showout=False)
            if rc != 0:
                cmd = 'weave launch'
                if peer:
                    cmd += ' %s' % peer
                self.cuisine.run(cmd, profile=True)

            env = self.cuisine.run('weave env', profile=True)
            ss = env[len('export'):].strip().split(' ')
            for entry in ss:
                splitted = entry.split('=')
                if len(splitted) == 2:
                    self.cuisine.bash.environSet(splitted[0],splitted[1])
                elif len(splitted) > 0:
                    self.cuisine.bash.environSet(splitted[0], '')
