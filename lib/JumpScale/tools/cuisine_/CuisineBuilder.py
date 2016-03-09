
from JumpScale import j


from ActionDecorator import ActionDecorator
from CuisineMongoCluster import mongoCluster


class actionrun(ActionDecorator):
    def __init__(self, *args, **kwargs):
        ActionDecorator.__init__(self, *args, **kwargs)
        self.selfobjCode = "cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.builder"


class CuisineBuilder(object):

    def __init__(self, executor, cuisine):
        self.executor = executor
        self.cuisine = cuisine
        self.bash = self.cuisine.bash
        self.mongoCluster = mongoCluster

    def all(self, start=False, sandbox=False, stor_addr=None):
        self.cuisine.installerdevelop.pip()
        self.cuisine.installerdevelop.python()
        self.cuisine.installerdevelop.jumpscale8()
        self.redis(start=start, force=True)
        self.core(start=start)
        self.syncthing(start=start)
        self.controller(start=start)
        self.fs(start=start)
        self.stor(start=start)
        self.etcd(start=start)
        self.cuisine.portal.install(start=start)
        self.mongodb(start=start)
        self.caddy(start=start)
        # self.skydns(start=start)
        self.influxdb(start=start)
        self.weave(start=start)
        if sandbox:
            if not stor_addr:
                raise RuntimeError("Store address should be specified if sandboxing enable.")
            self.sandbox(stor_addr)

    def sandbox(self, stor_addr, python=True):
        """
        stor_addr : addr to the store you want to populate. e.g.: https://stor.jumpscale.org/storx
        python : do you want to sandbox python too ? if you have segfault after trying sandboxing python, re run with python=False
        """
        # jspython is generated during install,need to copy it back into /opt before sandboxing
        self.cuisine.file_copy('/usr/local/bin/jspython', '/opt/jumpscale8/bin')

        # clean lib dir to avoid segfault during sandboxing
        self.cuisine.dir_remove('%s/*' % self.cuisine.dir_paths['libDir'])
        self.cuisine.dir_ensure('%s' % self.cuisine.dir_paths['libDir'])
        self.cuisine.file_link('/usr/local/lib/python3.5/dist-packages/JumpScale', '%s/JumpScale' % self.cuisine.dir_paths['libDir'])
        self.cuisine.file_link("%s/github/jumpscale/jumpscale_portal8/lib/portal" % self.cuisine.dir_paths["codeDir"], "%s/portal" % self.cuisine.dir_paths['jsLibDir'])

        # start sandboxing
        cmd = "j.tools.cuisine.local.builder.dedupe(['/opt'], 'js8_opt', '%s', sandbox_python=%s)" % (stor_addr, python)
        self.cuisine.run('js "%s"' % cmd)
        url_opt = '%s/static/js8_opt' % stor_addr

        return url_opt

    def _sandbox_python(self, python=True):
        print("START SANDBOX")
        if python:
            paths = []
            paths.append("/usr/lib/python3.5/")
            paths.append("/usr/local/lib/python3.5/dist-packages")
            paths.append("/usr/lib/python3/dist-packages")

            excludeFileRegex=["-tk/", "/lib2to3", "-34m-", ".egg-info"]
            excludeDirRegex=["/JumpScale", "\.dist-info", "config-x86_64-linux-gnu", "pygtk"]

            dest = j.sal.fs.joinPaths(self.cuisine.dir_paths['base'], 'lib')

            for path in paths:
                j.tools.sandboxer.copyTo(path, dest, excludeFileRegex=excludeFileRegex, excludeDirRegex=excludeDirRegex)

            if not j.sal.fs.exists("%s/bin/python" % self.cuisine.dir_paths['base']):
                j.sal.fs.copyFile("/usr/bin/python3.5", "%s/bin/python" % self.cuisine.dir_paths['base'])

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
            j.tools.sandboxer.dedupe(path, storpath=output_dir, name=namespace, reset=False, append=True, excludeDirs=['/opt/code'])

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
        cpath = self.cuisine.args_replace("$tmplsDir/cfg/caddy/caddyfile.conf")
        self.cuisine.dir_ensure("$tmplsDir/cfg/caddy")
        self.cuisine.dir_ensure("$tmplsDir/cfg/caddy/log/")
        self.cuisine.dir_ensure("$tmplsDir/cfg/caddy/www/")
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
    def stor(self, addr='0.0.0.0:8090', backend="$varDir/aydostor", start=True):
        """
        Build and Install aydostore
        @input addr, address and port on which the service need to listen. e.g. : 0.0.0.0:8090
        @input backend, directory where to save the data push to the store
        """
        self.cuisine.golang.install()
        self.cuisine.golang.get("github.com/g8os/stor", action=True)
        self.cuisine.file_copy(self.cuisine.joinpaths(self.cuisine.dir_paths['goDir'], 'bin', 'stor'), '$base/bin',action=True)
        self.cuisine.bash.addPath("$base/bin", action=True)

        self.cuisine.processmanager.stop("stor") # will also kill

        self.cuisine.dir_ensure("$cfgDir/stor")
        backend = self.cuisine.args_replace(backend)
        self.cuisine.dir_ensure(backend)
        config = {
            'listen_addr': addr,
            'store_root': backend,
        }
        content = j.data.serializer.toml.dumps(config)
        self.cuisine.file_write("$tmplsDir/cfg/stor/config.toml", content)


        if start:
            res = addr.split(":")
            if len(res) == 2:
                addr, port = res[0], res[1]
            else:
                addr, port = res[0], '8090'

                self.cuisine.fw.allowIncoming(port)
                if self.cuisine.process.tcpport_check(port,""):
                    raise RuntimeError("port %d is occupied, cannot start stor" % port)

            self.cuisine.file_copy("$tmplsDir/cfg/stor/config.toml", "$cfgDir/stor/")
            cmd = self.cuisine.bash.cmdGetPath("stor")
            self.cuisine.processmanager.ensure("stor", '%s --config $cfgDir/stor/config.toml' % cmd)

    @actionrun(action=True)
    def fs(self, start=False):
        content = """
        [[mount]]
            path="/opt"
            flist="/optvar/cfg/fs/js8_opt.flist"
            backend="opt"
            mode="RO"
            trim_base=true
        [backend]
        [backend.opt]
            path="/optvar/fs_backend/opt"
            stor="public"
            namespace="js8_opt"
            cleanup_cron="@every 1h"
            cleanup_older_than=24
            log=""
        [aydostor]
        [aydostor.public]
            addr="http://stor.jumpscale.org/storx"
            login=""
            passwd=""
        """
        self.cuisine.golang.install()
        self.cuisine.golang.get("github.com/g8os/fs", action=True)
        self.cuisine.dir_ensure("$tmplsDir/cfg/fs")
        self.cuisine.file_copy("$goDir/bin/fs", "$base/bin")
        self.cuisine.file_write("$goDir/src/github.com/g8os/fs/config/config.toml", content)
        self.cuisine.file_copy("$goDir/src/github.com/g8os/fs/config/config.toml", "$tmplsDir/cfg/fs")
        if start:
            self.cuisine.file_copy("$tmplsDir/cfg/fs", "$varDir/cfg", recursive=True)
            self.cuisine.processmanager.ensure('fs', cmd="$binDir/fs -c $varDir/cfg/fs/config.toml")


    @actionrun(action=True)
    def installdeps(self):
        self.cuisine.installer.base()
        self.cuisine.golang.install()
        self.cuisine.pip.upgrade('pip')
        self.cuisine.pip.install('pytoml')
        self.cuisine.pip.install('pygo')


    @actionrun(action=True)
    def syncthing(self, start=True):
        """
        build and setup syncthing to run on :8384 , this can be changed from the config file in /optvar/cfg/syncthing
        """
        self.installdeps()

        config="""
        <configuration version="11">
            <folder id="default" path="$homeDir/Sync" ro="false" rescanIntervalS="60" ignorePerms="false" autoNormalize="false">
                <device id="H7MBKSF-XNFETHA-2ERDXTB-JQCAXTA-BBTTLJN-23TN5BZ-4CL7KLS-FYCISAR"></device>
                <minDiskFreePct>1</minDiskFreePct>
                <versioning></versioning>
                <copiers>0</copiers>
                <pullers>0</pullers>
                <hashers>0</hashers>
                <order>random</order>
                <ignoreDelete>false</ignoreDelete>
            </folder>
            <device id="H7MBKSF-XNFETHA-2ERDXTB-JQCAXTA-BBTTLJN-23TN5BZ-4CL7KLS-FYCISAR" name="$hostname" compression="metadata" introducer="false">
                <address>dynamic</address>
            </device>
            <gui enabled="true" tls="false">
                <address>$lclAddrs:$port</address>
                <apikey>wbgjQX6uSgjI1RfS7BT1XQgvGX26DHMf</apikey>
            </gui>
            <options>
                <listenAddress>0.0.0.0:22000</listenAddress>
                <globalAnnounceServer>udp4://announce.syncthing.net:22026</globalAnnounceServer>
                <globalAnnounceServer>udp6://announce-v6.syncthing.net:22026</globalAnnounceServer>
                <globalAnnounceEnabled>true</globalAnnounceEnabled>
                <localAnnounceEnabled>true</localAnnounceEnabled>
                <localAnnouncePort>21025</localAnnouncePort>
                <localAnnounceMCAddr>[ff32::5222]:21026</localAnnounceMCAddr>
                <maxSendKbps>0</maxSendKbps>
                <maxRecvKbps>0</maxRecvKbps>
                <reconnectionIntervalS>60</reconnectionIntervalS>
                <startBrowser>true</startBrowser>
                <upnpEnabled>true</upnpEnabled>
                <upnpLeaseMinutes>60</upnpLeaseMinutes>
                <upnpRenewalMinutes>30</upnpRenewalMinutes>
                <upnpTimeoutSeconds>10</upnpTimeoutSeconds>
                <urAccepted>0</urAccepted>
                <urUniqueID></urUniqueID>
                <restartOnWakeup>true</restartOnWakeup>
                <autoUpgradeIntervalH>12</autoUpgradeIntervalH>
                <keepTemporariesH>24</keepTemporariesH>
                <cacheIgnoredFiles>true</cacheIgnoredFiles>
                <progressUpdateIntervalS>5</progressUpdateIntervalS>
                <symlinksEnabled>true</symlinksEnabled>
                <limitBandwidthInLan>false</limitBandwidthInLan>
                <databaseBlockCacheMiB>0</databaseBlockCacheMiB>
                <pingTimeoutS>30</pingTimeoutS>
                <pingIdleTimeS>60</pingIdleTimeS>
                <minHomeDiskFreePct>1</minHomeDiskFreePct>
            </options>
        </configuration>
        """
        #create config file
        content = self.cuisine.args_replace(config)
        content = content.replace("$lclAddrs",  "0.0.0.0", 1)
        content = content.replace ("$port", "8384", 1)

        self.cuisine.dir_ensure("$tmplsDir/cfg/syncthing/")
        self.cuisine.file_write("$tmplsDir/cfg/syncthing/config.xml", content)

        #build
        url = "https://github.com/syncthing/syncthing.git"
        self.cuisine.dir_remove('$goDir/src/github.com/syncthing/syncthing')
        dest = self.cuisine.git.pullRepo(url, branch="v0.11.25",  dest='$goDir/src/github.com/syncthing/syncthing', ssh=False)
        self.cuisine.run('cd %s && godep restore' % dest, profile=True)
        self.cuisine.run("cd %s && ./build.sh noupgrade" % dest, profile=True)

        #copy bin
        self.cuisine.file_copy(self.cuisine.joinpaths(dest, 'syncthing'), "$goDir/bin/", recursive=True)
        self.cuisine.file_copy("$goDir/bin/syncthing", "$binDir", recursive=True)

        if start:
            self._startSyncthing()

    @actionrun(action=True)
    def core(self,start=True, gid=None, nid=None):
        """
        builds and setsup dependencies of agent to run with the given gid and nid
        neither can be zero
        """
        #deps
        self.installdeps()
        self.redis(start=False)
        self.mongodb(start=False)
        #self.cuisine.installer.jumpscale8()

        self.syncthing(start=False)

        self.cuisine.tmux.killWindow("main", "core")

        self.cuisine.process.kill("core")

        self.cuisine.dir_ensure("$tmplsDir/cfg/core", recursive=True)
        self.cuisine.dir_ensure("$tmplsDir/cfg/core/conf", recursive=True)
        self.cuisine.dir_ensure("$tmplsDir/cfg/core/mid", recursive=True)

        url = "github.com/g8os/core"
        self.cuisine.golang.get(url)

        sourcepath = "$goDir/src/github.com/g8os/core"


        self.cuisine.run("cd %s && go build ." % sourcepath, profile=True)
        self.cuisine.file_move("%s/core" % sourcepath, "$binDir/core")

        # copy extensions
        self.cuisine.dir_remove("$tmplsDir/cfg/core/extensions")
        self.cuisine.file_copy("%s/extensions" % sourcepath, "$tmplsDir/cfg/core", recursive=True)
        self.cuisine.file_copy("%s/conf" % sourcepath, "$tmplsDir/cfg/core", recursive=True)
        self.cuisine.dir_ensure("$tmplsDir/cfg/core/extensions/syncthing")
        self.cuisine.file_copy("$binDir/syncthing", "$tmplsDir/cfg/core/extensions/syncthing/")




        # self.cuisine.dir_ensure("$cfgDir/agent8/agent8/conf", recursive=True)

        if start:
            self._startCore(nid, gid)

    @actionrun(action=True)
    def controller(self, start=True):
        """
        config: https://github.com/g8os/controller.git
        """
        #deps
        self.installdeps()
        self.redis(start=False)
        self.mongodb(start=False)
        self.syncthing(start=False)


        self.cuisine.processmanager.remove("agentcontroller8")
        pm = self.cuisine.processmanager.get("tmux")
        pm.stop("syncthing")

        self.cuisine.dir_ensure("$tmplsDir/cfg/controller", recursive=True)

        #get repo
        url = "github.com/g8os/controller"
        self.cuisine.golang.godep(url)

        sourcepath = "$goDir/src/github.com/g8os/controller"

        #do the actual building
        self.cuisine.run("cd %s && go build ." % sourcepath, profile=True)

        #move binary
        self.cuisine.file_move("%s/controller" % sourcepath, "$binDir/controller")



        #file copy
        self.cuisine.dir_remove("$tmplsDir/cfg/controller/extensions")
        self.cuisine.file_copy("%s/extensions" % sourcepath, "$tmplsDir/cfg/controller/extensions", recursive=True)

        if start:
            self._startController()


    def _startSyncthing(self):
        self.cuisine.dir_ensure("$cfgDir")
        self.cuisine.file_copy("$tmplsDir/cfg/syncthing/", "$cfgDir", recursive=True)

        GOPATH = self.cuisine.bash.environGet('GOPATH')
        env={}
        env["TMPDIR"]=self.cuisine.dir_paths["tmpDir"]
        pm = self.cuisine.processmanager.get("tmux")
        pm.ensure(name="syncthing", cmd="./syncthing -home  $cfgDir/syncthing", path=self.cuisine.joinpaths(GOPATH, "bin"))

    def _startCore(self, nid, gid):
        """
        if this is run on the sam e machine as a controller instance run controller first as the
        core will consume the avialable syncthing port and will cause a problem
        """
        if not nid:
            nid = 1
        if not gid:
            gid = 1

        self.cuisine.dir_ensure("$cfgDir/core/")
        self.cuisine.file_copy("$tmplsDir/cfg/core", "$cfgDir/", recursive=True)



        # manipulate config file
        sourcepath = "$binDir/core"
        C = self.cuisine.file_read("%s/agent.toml" % sourcepath)
        cfg = j.data.serializer.toml.loads(C)
        cfgdir = self.cuisine.dir_paths['cfgDir']
        cfg["main"]["message_ID_file"] = cfg["main"]["message_ID_file"].replace("./", self.cuisine.joinpaths(cfgdir,"/core/"))
        cfg["main"]["include"] = self.cuisine.joinpaths(cfgdir,"/core/conf")
        cfg["extensions"]["sync"]["cwd"] = cfg["extensions"]["sync"]["cwd"].replace("./", self.cuisine.joinpaths(cfgdir,"/core/"))
        cfg["extensions"]["jumpscript"]["cwd"] = cfg["extensions"]["jumpscript"]["cwd"].replace("./", self.cuisine.joinpaths(cfgdir,"/core/"))
        cfg["extensions"]["jumpscript_content"]["cwd"] = cfg["extensions"]["jumpscript_content"]["cwd"].replace("./", self.cuisine.joinpaths(cfgdir,"/core/"))
        cfg["extensions"]["js_daemon"]["cwd"] = cfg["extensions"]["js_daemon"]["cwd"].replace("./", self.cuisine.joinpaths(cfgdir,"/core/"))
        cfg["extensions"]["js_daemon"]["env"]["JUMPSCRIPTS_HOME"] = cfg["extensions"]["js_daemon"]["env"]["JUMPSCRIPTS_HOME"].replace("./", self.cuisine.joinpaths(cfgdir,"/core/"))
        cfg["logging"]["db"]["address"] = cfg["logging"]["db"]["address"].replace("./", self.cuisine.joinpaths(cfgdir,"/core/"))
        C = j.data.serializer.toml.dumps(cfg)

        self.cuisine.file_write("$cfgDir/core/agent.toml", C, replaceArgs=True)


        self._startMongodb()
        self._startRedis()
        self._startSyncthing()
        print("connection test ok to agentcontroller")
        #@todo (*1*) need to implement to work on node
        env={}
        env["TMPDIR"]=self.cuisine.dir_paths["tmpDir"]
        cmd = "$binDir/core -nid %s -gid %s -c $cfgDir/core/agent.toml" % (nid, gid)
        pm = self.cuisine.processmanager.get("tmux")
        pm.ensure("core", cmd=cmd, path="$cfgDir/core",  env=env)

    def _startController(self):
        import re
        import hashlib
        import time
        self.cuisine.dir_ensure("$cfgDir/controller/")
        self.cuisine.file_copy("$tmplsDir/cfg/controller", "$cfgDir/", recursive=True)


        #edit config
        sourcepath = "$goDir/src/github.com/g8os/controller"
        C = self.cuisine.file_read("%s/agentcontroller.toml"%sourcepath)
        cfg = j.data.serializer.toml.loads(C)

        cfgDir = self.cuisine.dir_paths['cfgDir']
        cfg["events"]["python_path"] = cfg["events"]["python_path"].replace("./",self.cuisine.joinpaths(cfgDir, "/controller/"))
        cfg["processor"]["python_path"] = cfg["processor"]["python_path"].replace("./",self.cuisine.joinpaths(cfgDir, "/controller/"))
        cfg["jumpscripts"]["python_path"] = cfg["jumpscripts"]["python_path"].replace("./",self.cuisine.joinpaths(cfgDir, "/controller/"))
        cfg["jumpscripts"]["settings"]["jumpscripts_path"] = cfg["jumpscripts"]["settings"]["jumpscripts_path"].replace("./",self.cuisine.joinpaths(cfgDir, "/controller/"))
        C = j.data.serializer.toml.dumps(cfg)

        self.cuisine.file_write('$cfgDir/controller/agentcontroller.toml', C, replaceArgs=True)

        #expose syncthing and get api key
        sync_cfg = self.cuisine.file_read("$tmplsDir/cfg/syncthing/config.xml")
        sync_conn = re.search(r'<address>([0-9.]+):([0-9]+)</', sync_cfg)
        apikey = re.search(r'<apikey>([\w\-]+)</apikey>', sync_cfg).group(1)
        sync_cfg = sync_cfg.replace(sync_conn.group(1), "0.0.0.0")
        sync_cfg = sync_cfg.replace(sync_conn.group(2), "18384")
        self.cuisine.file_write("$cfgDir/syncthing/config.xml", sync_cfg)

        #add jumpscripts file
        self._startSyncthing()

        if not self.cuisine.executor.type == 'local':
            synccl = j.clients.syncthing.get(addr=self.executor.addr, sshport=self.executor.port, port=18384, apikey=apikey)
        else:
            synccl = j.clients.syncthing.get(addr="localhost", port=18384, apikey=apikey)

        jumpscripts_path = self.cuisine.args_replace("$cfgDir/cfg/controller/jumpscripts")
        for i in range(4):
            try:
                jumpscripts_id = "jumpscripts-%s" % hashlib.md5(synccl.id_get().encode()).hexdigest()
                break
            except RuntimeError:
                print("restablishing connection to syncthing")
        else:
            raise RuntimeError('Syncthing is not responding. Exiting.')

        synccl.config_add_folder(jumpscripts_id, jumpscripts_path)

        #start
        self._startMongodb()
        self._startRedis()
        env = {}
        env["TMPDIR"] = self.cuisine.dir_paths["tmpDir"]
        cmd = "$binDir/controller -c $cfgDir/controller/agentcontroller.toml"
        pm = self.cuisine.processmanager.get("tmux")
        pm.ensure("controller", cmd=cmd, path="$cfgDir/controller/", env=env)

    def _startRedis(self, name="main"):
        dpath,cpath=j.clients.redis._getPaths(name)
        cmd="$binDir/redis-server %s"%cpath
        self.cuisine.processmanager.ensure(name="redis_%s" % name,cmd=cmd,env={},path='$binDir')

    def _startMongodb(self, name="mongod"):
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
        self.cuisine.run_script(C,profile=True, action=True)
        self.cuisine.bash.addPath("$base/bin", action=True)

        if start:
            self.cuisine.process.kill("etcd")
            if host and peers:
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
            cp -f $tmpDir/build/redis/redis-3.0.6/src/redis-server $base/bin/
            cp -f $tmpDir/build/redis/redis-3.0.6/src/redis-cli $base/bin/

            rm -rf $base/apps/redis
            """
            C=self.cuisine.bash.replaceEnvironInText(C)
            C=self.cuisine.args_replace(C)
            self.cuisine.run_script(C, profile=True)
        else:
            if self.cuisine.command_check("redis-server")==False:
                self.cuisine.package.install("redis")
            cmd=self.cuisine.command_location("redis-server")
            dest="%s/redis-server"%self.cuisine.dir_paths["binDir"]
            if cmd!=dest:
                self.cuisine.file_copy(cmd,dest)

        self.cuisine.bash.addPath(j.sal.fs.joinPaths(self.cuisine.dir_paths["base"], "bin"), action=True)

        j.clients.redis.executor=self.executor
        j.clients.redis.cuisine=self.cuisine
        j.clients.redis.configureInstance(name, ip, port, maxram=maxram, appendonly=appendonly, \
            snapshot=snapshot, slave=slave, ismaster=ismaster, passwd=passwd, unixsocket=True)

        if start:
            self._startRedis(name)

    @actionrun(action=True)
    def mongodb(self, start=True):
        self.cuisine.installer.base()
        exists = self.cuisine.command_check("mongod")

        if exists:
            cmd = self.cuisine.command_location("mongod")
            dest = "%s/mongod" % self.cuisine.dir_paths["binDir"]
            if j.sal.fs.pathClean(cmd) != j.sal.fs.pathClean(dest):
                self.cuisine.file_copy(cmd, dest)
        else:
            appbase = self.cuisine.dir_paths["binDir"]

            url = None
            if self.cuisine.isUbuntu:
                url = 'https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu1404-3.2.1.tgz'
            elif self.cuisine.isArch:
                self.cuisine.package.install("mongodb")
            elif self.cuisine.isMac: #@todo better platform mgmt
                url = 'https://fastdl.mongodb.org/osx/mongodb-osx-x86_64-3.2.1.tgz'
            else:
                raise RuntimeError("unsupported platform")
                return

            if url:
                self.cuisine.file_download(url, to="$tmpDir", overwrite=False, expand=True)
                tarpath = self.cuisine.fs_find("$tmpDir", recursive=True, pattern="*mongodb*.tgz", type='f')[0]
                self.cuisine.file_expand(tarpath,"$tmpDir")
                extracted = self.cuisine.fs_find("$tmpDir", recursive=True, pattern="*mongodb*", type='d')[0]
                for file in self.cuisine.fs_find('%s/bin/' % extracted, type='f'):
                    self.cuisine.file_copy(file, appbase)

        self.cuisine.dir_ensure('$varDir/data/db')

        if start:
            self._startMongodb("mongod")

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
