
from JumpScale import j


from ActionDecorator import ActionDecorator
from CuisineMongoCluster import mongoCluster
import time

"""
please ensure that the start and build methods are separate and
the build doesnt place anyfile outside opt as it will be used in aysfs mounted system
"""

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
        if not self.cuisine.executor.type == 'local':
            self.cuisine.installerdevelop.jumpscale8()
        self.cuisine.portal.install(start=start)
        self.redis(start=start, force=True)
        self.core(start=start)
        self.syncthing(start=start)
        self.controller(start=start)
        self.fs(start=start)
        self.stor(start=start)
        self.etcd(start=start)
        self.mongodb(start=start)
        self.caddy(start=start)
        # self.skydns(start=start)
        self.influxdb(start=start)
        self.weave(start=start)
        if sandbox:
            if not stor_addr:
                raise j.exceptions.RuntimeError("Store address should be specified if sandboxing enable.")
            self.sandbox(stor_addr)

    def sandbox(self, stor_addr, python=True):
        """
        stor_addr : addr to the store you want to populate. e.g.: https://stor.jumpscale.org/storx
        python : do you want to sandbox python too ? if you have segfault after trying sandboxing python, re run with python=False
        """
        # jspython is generated during install,need to copy it back into /opt before sandboxing
        self.cuisine.core.file_copy('/usr/local/bin/jspython', '/opt/jumpscale8/bin')

        # clean lib dir to avoid segfault during sandboxing
        self.cuisine.core.dir_remove('%s/*' % self.cuisine.core.dir_paths['libDir'])
        self.cuisine.core.dir_ensure('%s' % self.cuisine.core.dir_paths['libDir'])
        self.cuisine.core.file_link('/usr/local/lib/python3.5/dist-packages/JumpScale', '%s/JumpScale' % self.cuisine.core.dir_paths['libDir'])
        self.cuisine.core.file_link("%s/github/jumpscale/jumpscale_portal8/lib/portal" % self.cuisine.core.dir_paths["codeDir"], "%s/portal" % self.cuisine.core.dir_paths['jsLibDir'])

        # start sandboxing
        cmd = "j.tools.cuisine.local.builder.dedupe(['/opt'], 'js8_opt', '%s', sandbox_python=%s)" % (stor_addr, python)
        self.cuisine.core.run('js "%s"' % cmd)
        url_opt = '%s/static/js8_opt.flist' % stor_addr

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

            dest = j.sal.fs.joinPaths(self.cuisine.core.dir_paths['base'], 'lib')

            for path in paths:
                j.tools.sandboxer.copyTo(path, dest, excludeFileRegex=excludeFileRegex, excludeDirRegex=excludeDirRegex)

            if not j.sal.fs.exists("%s/bin/python" % self.cuisine.core.dir_paths['base']):
                j.sal.fs.copyFile("/usr/bin/python3.5", "%s/bin/python" % self.cuisine.core.dir_paths['base'])

        j.tools.sandboxer.sandboxLibs("%s/lib" % self.cuisine.core.dir_paths['base'], recursive=True)
        j.tools.sandboxer.sandboxLibs("%s/bin" % self.cuisine.core.dir_paths['base'], recursive=True)
        print("SANDBOXING DONE, ALL OK IF TILL HERE, A Segfault can happen because we have overwritten ourselves.")

    def dedupe(self, dedupe_path, namespace, store_addr, output_dir='/tmp/sandboxer', sandbox_python=True):
        self.cuisine.core.dir_remove(output_dir)

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
            raise j.exceptions.RuntimeError('some files didnt upload properly. %s' % ("\n".join(error_files)))

        metadataPath = j.sal.fs.joinPaths(output_dir, "md", "%s.flist" % namespace)
        print('uploading %s' % metadataPath)
        store_client.putStaticFile(namespace+".flist", metadataPath)

    @actionrun(action=True)
    def skydns(self,start=True):
        self.cuisine.golang.install()
        self.cuisine.golang.get("github.com/skynetservices/skydns",action=True)
        self.cuisine.core.file_copy(self.cuisine.core.joinpaths('$goDir', 'bin', 'skydns'), '$binDir', action=True)
        self.cuisine.bash.addPath(self.cuisine.core.args_replace("$binDir"), action=True)

        if start:
            self._startSkydns()

    @actionrun(action=True)
    def caddy(self,ssl=False,start=True, dns=None):
        self.cuisine.golang.install()
        self.cuisine.golang.get("github.com/mholt/caddy",action=True)
        self.cuisine.core.file_copy(self.cuisine.core.joinpaths('$goDir', 'bin', 'caddy'), '$binDir', action=True)
        self.cuisine.bash.addPath(self.cuisine.core.args_replace("$binDir"), action=True)

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
        C = self.cuisine.core.args_replace(C)
        cpath = self.cuisine.core.args_replace("$tmplsDir/cfg/caddy/caddyfile.conf")
        self.cuisine.core.dir_ensure("$tmplsDir/cfg/caddy")
        self.cuisine.core.dir_ensure("$tmplsDir/cfg/caddy/log/")
        self.cuisine.core.dir_ensure("$tmplsDir/cfg/caddy/www/")
        self.cuisine.core.file_write(cpath, C)

        if start:
            self._startCaddy(ssl)


    def caddyConfig(self,sectionname,config):
        """
        config format see https://caddyserver.com/docs/caddyfile
        """
        raise j.exceptions.RuntimeError("needs to be implemented")
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
        self.cuisine.core.file_copy(self.cuisine.core.joinpaths(self.cuisine.core.dir_paths['goDir'], 'bin', 'stor'), '$base/bin',action=True)
        self.cuisine.bash.addPath("$base/bin", action=True)

        self.cuisine.processmanager.stop("stor") # will also kill

        self.cuisine.core.dir_ensure("$cfgDir/stor")
        backend = self.cuisine.core.args_replace(backend)
        self.cuisine.core.dir_ensure(backend)
        config = {
            'listen_addr': addr,
            'store_root': backend,
        }
        content = j.data.serializer.toml.dumps(config)
        self.cuisine.core.file_write("$tmplsDir/cfg/stor/config.toml", content)

        if start:
            self._startStor(addr)

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
        self.cuisine.core.dir_ensure("$tmplsDir/cfg/fs")
        self.cuisine.core.file_copy("$goDir/bin/fs", "$base/bin")
        self.cuisine.core.file_write("$goDir/src/github.com/g8os/fs/config/config.toml", content)
        self.cuisine.core.file_copy("$goDir/src/github.com/g8os/fs/config/config.toml", "$tmplsDir/cfg/fs")
        if start:
            self._startFs()



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
        content = self.cuisine.core.args_replace(config)
        content = content.replace("$lclAddrs",  "0.0.0.0", 1)
        content = content.replace ("$port", "8384", 1)

        self.cuisine.core.dir_ensure("$tmplsDir/cfg/syncthing/")
        self.cuisine.core.file_write("$tmplsDir/cfg/syncthing/config.xml", content)

        #build
        url = "https://github.com/syncthing/syncthing.git"
        self.cuisine.core.dir_remove('$goDir/src/github.com/syncthing/syncthing')
        dest = self.cuisine.git.pullRepo(url, branch="v0.11.25",  dest='$goDir/src/github.com/syncthing/syncthing', ssh=False, depth=None)
        self.cuisine.core.run('cd %s && godep restore' % dest, profile=True)
        self.cuisine.core.run("cd %s && ./build.sh noupgrade" % dest, profile=True)

        #copy bin
        self.cuisine.core.file_copy(self.cuisine.core.joinpaths(dest, 'syncthing'), "$goDir/bin/", recursive=True)
        self.cuisine.core.file_copy("$goDir/bin/syncthing", "$binDir", recursive=True)

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

        self.cuisine.core.dir_ensure("$tmplsDir/cfg/core", recursive=True)
        self.cuisine.core.file_ensure("$tmplsDir/cfg/core/.mid")

        url = "github.com/g8os/core"
        self.cuisine.golang.godep(url)

        sourcepath = "$goDir/src/github.com/g8os/core"


        self.cuisine.core.run("cd %s && go build ." % sourcepath, profile=True)
        self.cuisine.core.file_move("%s/core" % sourcepath, "$binDir/core")


        # copy extensions
        self.cuisine.core.dir_remove("$tmplsDir/cfg/core/extensions")
        self.cuisine.core.file_copy("%s/extensions" % sourcepath, "$tmplsDir/cfg/core", recursive=True)
        self.cuisine.core.file_copy("%s/g8os.toml" % sourcepath, "$tmplsDir/cfg/core")
        self.cuisine.core.dir_ensure("$tmplsDir/cfg/core/conf/")
        self.cuisine.core.file_copy("{0}sshd.toml {0}basic.toml {0}sshd.toml".format(sourcepath+"/conf/"), "$tmplsDir/cfg/core/conf/", recursive=True)
        self.cuisine.core.file_copy("%s/network.toml" % sourcepath, "$tmplsDir/cfg/core")
        self.cuisine.core.file_copy("%s/conf" % sourcepath, "$tmplsDir/cfg/core", recursive=True)
        self.cuisine.core.dir_ensure("$tmplsDir/cfg/core/extensions/syncthing")
        self.cuisine.core.file_copy("$binDir/syncthing", "$tmplsDir/cfg/core/extensions/syncthing/") 




        # self.cuisine.core.dir_ensure("$cfgDir/agent8/agent8/conf", recursive=True)

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

        self.cuisine.core.dir_ensure("$tmplsDir/cfg/controller", recursive=True)

        #get repo
        url = "github.com/g8os/controller"
        self.cuisine.golang.godep(url)

        sourcepath = "$goDir/src/github.com/g8os/controller"

        #do the actual building
        self.cuisine.core.run("cd %s && go build ." % sourcepath, profile=True)

        #move binary
        self.cuisine.core.file_move("%s/controller" % sourcepath, "$binDir/controller")



        #file copy
        self.cuisine.core.dir_remove("$tmplsDir/cfg/controller/extensions")
        self.cuisine.core.file_copy("%s/github/jumpscale/jumpscale_core8/apps/agentcontroller/jumpscripts/jumpscale" % self.cuisine.core.dir_paths["codeDir"], "$tmplsDir/cfg/controller/jumpscripts/", recursive=True)
        self.cuisine.core.file_copy("%s/extensions" % sourcepath, "$tmplsDir/cfg/controller/extensions", recursive=True)

        if start:
            self._startController()

    def _startCaddy(self, ssl):
        cpath = self.cuisine.core.args_replace("$tmplsDir/cfg/caddy/caddyfile.conf")
        self.cuisine.processmanager.stop("caddy")  # will also kill
        if ssl:
            self.cuisine.fw.allowIncoming(443)
            self.cuisine.fw.allowIncoming(80)

            if self.cuisine.process.tcpport_check(80,"") or self.cuisine.process.tcpport_check(443,""):
                raise j.exceptions.RuntimeError("port 80 or 443 are occupied, cannot install caddy")

        else:
            if self.cuisine.process.tcpport_check(80,""):
                raise j.exceptions.RuntimeError("port 80 is occupied, cannot install caddy")

            PORTS = ":80"
            self.cuisine.fw.allowIncoming(80)
        cmd = self.cuisine.bash.cmdGetPath("caddy")
        self.cuisine.processmanager.ensure("caddy", '%s -conf=%s -email=info@greenitglobe.com' % (cmd, cpath))

    def _startSkydns(self):
        cmd = self.cuisine.bash.cmdGetPath("skydns")
        self.cuisine.processmanager.ensure("skydns",cmd + " -addr 0.0.0.0:53")

    def _startFs(self):
        self.cuisine.core.file_copy("$tmplsDir/cfg/fs", "$cfgDir", recursive=True)
        self.cuisine.processmanager.ensure('fs', cmd="$binDir/fs -c $cfgDir/fs/config.toml")

    def _startSyncthing(self):
        self.cuisine.core.dir_ensure("$cfgDir")
        self.cuisine.core.file_copy("$tmplsDir/cfg/syncthing/", "$cfgDir", recursive=True)

        GOPATH = self.cuisine.bash.environGet('GOPATH')
        env={}
        env["TMPDIR"]=self.cuisine.core.dir_paths["tmpDir"]
        pm = self.cuisine.processmanager.get("tmux")
        pm.ensure(name="syncthing", cmd="./syncthing -home  $cfgDir/syncthing", path=self.cuisine.core.joinpaths(GOPATH, "bin"))

    def _startStor(self, addr):
        res = addr.split(":")
        if len(res) == 2:
            addr, port = res[0], res[1]
        else:
            addr, port = res[0], '8090'

            self.cuisine.fw.allowIncoming(port)
            if self.cuisine.process.tcpport_check(port,""):
                raise j.exceptions.RuntimeError("port %d is occupied, cannot start stor" % port)

        self.cuisine.core.dir_ensure("$cfgDir/stor/", recursive=True)
        self.cuisine.core.file_copy("$tmplsDir/cfg/stor/config.toml", "$cfgDir/stor/")
        cmd = self.cuisine.bash.cmdGetPath("stor")
        self.cuisine.processmanager.ensure("stor", '%s --config $cfgDir/stor/config.toml' % cmd)

    def _startCore(self, nid, gid, controller_url="http://127.0.0.1:8966"):
        """
        if this is run on the sam e machine as a controller instance run controller first as the
        core will consume the avialable syncthing port and will cause a problem
        """

        # @todo this will break code if two instances on same machine
        if not nid:
            nid = 1
        if not gid:
            gid = 1

        self.cuisine.core.dir_ensure("$cfgDir/core/")
        self.cuisine.core.file_copy("$tmplsDir/cfg/core", "$cfgDir/", recursive=True)



        # manipulate config file
        sourcepath = "$tmplsDir/cfg/core"
        C = self.cuisine.core.file_read("%s/g8os.toml" % sourcepath)
        cfg = j.data.serializer.toml.loads(C)
        cfgdir = self.cuisine.core.dir_paths['cfgDir']
        cfg["main"]["message_ID_file"] = self.cuisine.core.joinpaths(cfgdir,"/core/.mid")
        cfg["main"]["include"] = self.cuisine.core.joinpaths(cfgdir,"/core/conf")
        cfg["main"].pop("network")
        cfg["controllers"] = {"main": {"url": controller_url}}
        cfg["extension"]["sync"]["cwd"] = self.cuisine.core.joinpaths(cfgdir,"/core/extensions")
        cfg["extension"]["jumpscript"]["cwd"] = self.cuisine.core.joinpaths(cfgdir,"/core/extensions/jumpscript")
        cfg["extension"]["jumpscript_content"]["cwd"] = self.cuisine.core.joinpaths(cfgdir,"/core/extensions/jumpscript")
        cfg["extension"]["js_daemon"]["cwd"] = self.cuisine.core.joinpaths(cfgdir,"/core/extensions/jumpscript")
        cfg["extension"]["js_daemon"]["env"]["JUMPSCRIPTS_HOME"] = self.cuisine.core.joinpaths(cfgdir,"/core/jumpscripts/")
        cfg["logging"]["db"]["address"] = self.cuisine.core.joinpaths(cfgdir,"/core/logs")
        C = j.data.serializer.toml.dumps(cfg)

        self.cuisine.core.file_write("$cfgDir/core/g8os.toml", C, replaceArgs=True)


        self._startMongodb()
        self._startRedis()
        print("connection test ok to agentcontroller")
        #@todo (*1*) need to implement to work on node
        env={}
        env["TMPDIR"]=self.cuisine.core.dir_paths["tmpDir"]
        cmd = "$binDir/core -nid %s -gid %s -c $cfgDir/core/g8os.toml" % (nid, gid)
        pm = self.cuisine.processmanager.get("tmux")
        pm.ensure("core", cmd=cmd, path="$cfgDir/core",  env=env)

    def _startController(self):
        import re
        import hashlib
        import time
        self.cuisine.core.dir_ensure("$cfgDir/controller/")
        self.cuisine.core.file_copy("$tmplsDir/cfg/controller", "$cfgDir/", recursive=True)


        #edit config
        sourcepath = "$goDir/src/github.com/g8os/controller"
        C = self.cuisine.core.file_read("%s/agentcontroller.toml"%sourcepath)
        cfg = j.data.serializer.toml.loads(C)

        cfgDir = self.cuisine.core.dir_paths['cfgDir']
        cfg["events"]["python_path"] = self.cuisine.core.joinpaths(cfgDir, "/controller/extensions:/opt/jumpscale8/lib")
        cfg["processor"]["python_path"] = self.cuisine.core.joinpaths(cfgDir, "/controller/extensions:/opt/jumpscale8/lib")
        cfg["jumpscripts"]["python_path"] = self.cuisine.core.joinpaths(cfgDir, "/controller/extensions:/opt/jumpscale8/lib")
        cfg["jumpscripts"]["settings"]["jumpscripts_path"] = self.cuisine.core.joinpaths(cfgDir, "/controller/jumpscripts")
        C = j.data.serializer.toml.dumps(cfg)

        self.cuisine.core.file_write('$cfgDir/controller/agentcontroller.toml', C, replaceArgs=True)

        #expose syncthing and get api key
        sync_cfg = self.cuisine.core.file_read("$tmplsDir/cfg/syncthing/config.xml")
        sync_conn = re.search(r'<address>([0-9.]+):([0-9]+)</', sync_cfg)
        apikey = re.search(r'<apikey>([\w\-]+)</apikey>', sync_cfg).group(1)
        sync_cfg = sync_cfg.replace(sync_conn.group(1), "0.0.0.0")
        sync_cfg = sync_cfg.replace(sync_conn.group(2), "18384")
        self.cuisine.core.file_write("$cfgDir/syncthing/config.xml", sync_cfg)

        # add jumpscripts file
        self._startSyncthing()

        if not self.cuisine.executor.type == 'local':
            synccl = j.clients.syncthing.get(addr=self.executor.addr, sshport=self.executor.port, port=18384, apikey=apikey)
        else:
            synccl = j.clients.syncthing.get(addr="localhost", port=18384, apikey=apikey)

        jumpscripts_path = self.cuisine.core.args_replace("$cfgDir/controller/jumpscripts")
        timeout = 30
        start = time.time()
        syn_id = None
        while time.time() < (start + timeout) and syn_id is None:
            try:
                syn_id = synccl.id_get()
            except RuntimeError:
                print("restablishing connection to syncthing")

        if syn_id is None:
            raise j.exceptions.RuntimeError('Syncthing is not responding. Exiting.')

        jumpscripts_id = "jumpscripts-%s" % hashlib.md5(syn_id.encode()).hexdigest()
        synccl.config_add_folder(jumpscripts_id, jumpscripts_path)

        #start
        self._startMongodb()
        self._startRedis()
        env = {}
        env["TMPDIR"] = self.cuisine.core.dir_paths["tmpDir"]
        cmd = "$binDir/controller -c $cfgDir/controller/agentcontroller.toml"
        pm = self.cuisine.processmanager.get("tmux")
        pm.ensure("controller", cmd=cmd, path="$cfgDir/controller/", env=env)

    def _startRedis(self, name="main"):
        dpath,cpath=j.clients.redis._getPaths(name)
        cmd="$binDir/redis-server %s"%cpath
        self.cuisine.processmanager.ensure(name="redis_%s" % name,cmd=cmd,env={},path='$binDir')

    def _startMongodb(self, name="mongod"):
        which = self.cuisine.core.command_location("mongod")
        self.cuisine.core.dir_ensure('$varDir/data/mongodb')
        cmd="%s --dbpath $varDir/data/mongodb" % which
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
        self.cuisine.core.run_script(C,profile=True, action=True)
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
        if not self.cuisine.core.isMac:

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
            C=self.cuisine.core.args_replace(C)
            self.cuisine.core.run_script(C,profile=True)
            #move action
            C="""
            set -ex
            mkdir -p $base/bin/
            cp -f $tmpDir/build/redis/redis-3.0.6/src/redis-server $base/bin/
            cp -f $tmpDir/build/redis/redis-3.0.6/src/redis-cli $base/bin/

            rm -rf $base/apps/redis
            """
            C=self.cuisine.bash.replaceEnvironInText(C)
            C=self.cuisine.core.args_replace(C)
            self.cuisine.core.run_script(C, profile=True)
        else:
            if self.cuisine.core.command_check("redis-server")==False:
                self.cuisine.package.install("redis")
            cmd=self.cuisine.core.command_location("redis-server")
            dest="%s/redis-server"%self.cuisine.core.dir_paths["binDir"]
            if cmd!=dest:
                self.cuisine.core.file_copy(cmd,dest)

        self.cuisine.bash.addPath(j.sal.fs.joinPaths(self.cuisine.core.dir_paths["base"], "bin"), action=True)

        j.clients.redis.executor=self.executor
        j.clients.redis.cuisine=self.cuisine
        j.clients.redis.configureInstance(name, ip, port, maxram=maxram, appendonly=appendonly, \
            snapshot=snapshot, slave=slave, ismaster=ismaster, passwd=passwd, unixsocket=True)

        if start:
            self._startRedis(name)

    @actionrun(action=True)
    def mongodb(self, start=True):
        self.cuisine.installer.base()
        exists = self.cuisine.core.command_check("mongod")

        if exists:
            cmd = self.cuisine.core.command_location("mongod")
            dest = "%s/mongod" % self.cuisine.core.dir_paths["binDir"]
            if j.sal.fs.pathClean(cmd) != j.sal.fs.pathClean(dest):
                self.cuisine.core.file_copy(cmd, dest)
        else:
            appbase = self.cuisine.core.dir_paths["binDir"]

            url = None
            if self.cuisine.core.isUbuntu:
                url = 'https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu1404-3.2.1.tgz'
            elif self.cuisine.core.isArch:
                self.cuisine.package.install("mongodb")
            elif self.cuisine.core.isMac: #@todo better platform mgmt
                url = 'https://fastdl.mongodb.org/osx/mongodb-osx-x86_64-3.2.1.tgz'
            else:
                raise j.exceptions.RuntimeError("unsupported platform")
                return

            if url:
                self.cuisine.core.file_download(url, to="$tmpDir", overwrite=False, expand=True)
                tarpath = self.cuisine.core.fs_find("$tmpDir", recursive=True, pattern="*mongodb*.tgz", type='f')[0]
                self.cuisine.core.file_expand(tarpath,"$tmpDir")
                extracted = self.cuisine.core.fs_find("$tmpDir", recursive=True, pattern="*mongodb*", type='d')[0]
                for file in self.cuisine.core.fs_find('%s/bin/' % extracted, type='f'):
                    self.cuisine.core.file_copy(file, appbase)

        self.cuisine.core.dir_ensure('$varDir/data/mongodb')

        if start:
            self._startMongodb("mongod")

    def influxdb(self, start=True):
        self.cuisine.installer.base()

        if self.cuisine.core.isMac:
            self.cuisine.package.mdupdate()
            self.cuisine.package.install('influxdb')
        if self.cuisine.core.isUbuntu:
            self.cuisine.core.dir_ensure("$tmplsDir/cfg/influxdb")
            C= """
cd $tmpDir
wget https://s3.amazonaws.com/influxdb/influxdb-0.10.0-1_linux_amd64.tar.gz
tar xvfz influxdb-0.10.0-1_linux_amd64.tar.gz
cp influxdb-0.10.0-1/usr/bin/influxd $binDir
cp influxdb-0.10.0-1/etc/influxdb/influxdb.conf $tmplsDir/cfg/influxdb/influxdb.conf"""
            C = self.cuisine.bash.replaceEnvironInText(C)
            C = self.cuisine.core.args_replace(C)
            self.cuisine.core.run_script(C, profile=True, action=True)
            self.cuisine.bash.addPath(self.cuisine.core.args_replace("$binDir"), action=True)

        if start:
            self._start_influxdb()

    def _start_influxdb(self):
        binPath = self.cuisine.bash.cmdGetPath('influxd')
        self.cuisine.core.dir_ensure("$varDir/data/influxdb")
        self.cuisine.core.dir_ensure("$varDir/data/influxdb/meta")
        self.cuisine.core.dir_ensure("$varDir/data/influxdb/data")
        self.cuisine.core.dir_ensure("$varDir/data/influxdb/wal")
        content = self.cuisine.core.file_read('$tmplsDir/cfg/influxdb/influxdb.conf')
        cfg = j.data.serializer.toml.loads(content)
        cfg['meta']['dir'] = "$varDir/data/influxdb/meta"
        cfg['data']['dir'] = "$varDir/data/influxdb/data"
        cfg['data']['wal-dir'] = "$varDir/data/influxdb/data"
        self.cuisine.core.dir_ensure('$cfgDir/influxdb')
        self.cuisine.core.file_write('$cfgDir/influxdb/influxdb.conf', j.data.serializer.toml.dumps(cfg))
        cmd = "%s -config $cfgDir/influxdb/influxdb.conf" % (binPath)
        self.cuisine.process.kill("influxdb")
        self.cuisine.processmanager.ensure("influxdb", cmd=cmd, env={}, path="")

    def grafana(self, start=True, influx_addr='127.0.0.1', influx_port=8086, port=3000):

        if self.cuisine.core.isUbuntu:
            dataDir = self.cuisine.core.args_replace("$varDir/data/grafana")
            logDir = '%s/log' %(dataDir)
            C= """
cd $tmpDir
wget https://grafanarel.s3.amazonaws.com/builds/grafana-2.6.0.linux-x64.tar.gz
tar -xvzf grafana-2.6.0.linux-x64.tar.gz
cd grafana-2.6.0
cp bin/grafana-server $binDir
mkdir -p $tmplsDir/cfg/grafana
cp -rn conf public vendor $tmplsDir/cfg/grafana
mkdir -p %s
"""%(logDir)

            C = self.cuisine.bash.replaceEnvironInText(C)
            C = self.cuisine.core.args_replace(C)
            self.cuisine.core.run_script(C, profile=True, action=True)
            self.cuisine.bash.addPath(self.cuisine.core.args_replace("$binDir"), action=True)
            cfg = self.cuisine.core.file_read("$tmplsDir/cfg/grafana/conf/defaults.ini")
            cfg = cfg.replace('data = data', 'data = %s'%(dataDir))
            cfg = cfg.replace('logs = data/log', 'logs = %s'%(logDir))
            self.cuisine.core.file_write("$tmplsDir/cfg/cfg/grafana/conf/defaults.ini", cfg)
            scriptedagent = """/* global _ */

/*
 * Complex scripted dashboard
 * This script generates a dashboard object that Grafana can load. It also takes a number of user
 * supplied URL parameters (in the ARGS variable)
 *
 * Return a dashboard object, or a function
 *
 * For async scripts, return a function, this function must take a single callback function as argument,
 * call this callback function with the dashboard object (look at scripted_async.js for an example)
 */

'use strict';

// accessible variables in this scope
var window, document, ARGS, $, jQuery, moment, kbn;

// Setup some variables
var dashboard;

// All url parameters are available via the ARGS object
var ARGS;

// Intialize a skeleton with nothing but a rows array and service object
dashboard = {
  rows : [],
  refresh: '5s',
};

// Set a title
dashboard.title = 'Scripted dash';

// Set default time
// time can be overriden in the url using from/to parameters, but this is
// handled automatically in grafana core during dashboard initialization
dashboard.time = {
  from: "now-6h",
  to: "now"
};

var series = [];

if(!_.isUndefined(ARGS.series)) {
  series = ARGS.series.split(',');
}


dashboard.rows.push({
    panels: [
{
  "aliasColors": {},
  "bars": false,
  "datasource": 'influxdb_main',
  "editable": true,
  "error": false,
  "fill": 1,
  "grid": {
    "leftLogBase": 1,
    "leftMax": null,
    "leftMin": null,
    "rightLogBase": 1,
    "rightMax": null,
    "rightMin": null,
    "threshold1": null,
    "threshold1Color": "rgba(216, 200, 27, 0.27)",
    "threshold2": null,
    "threshold2Color": "rgba(234, 112, 112, 0.22)"
  },
  "hideTimeOverride": false,
  "id": 1,
  "isNew": true,
  "legend": {
    "avg": false,
    "current": false,
    "max": false,
    "min": false,
    "show": true,
    "total": false,
    "values": false
  },
  "lines": true,
  "linewidth": 2,
  "links": [],
  "nullPointMode": "connected",
  "percentage": false,
  "pointradius": 5,
  "points": false,
  "renderer": "flot",
  "seriesOverrides": [],
  "span": 12,
  "stack": false,
  "steppedLine": false,
  "targets": series.map(function(x){return {
      "dsType": "influxdb",
      "groupBy": [
        {
          "params": [
            "auto"
          ],
          "type": "time"
        },
        {
          "params": [
            "null"
          ],
          "type": "fill"
        }
      ],
      "hide": false,
      "measurement": x,
      "query": 'SELECT "value" FROM "'+x+'"',
      "rawQuery": true,
      "refId": "A",
      "resultFormat": "time_series",
      "select": [
        [
          {
            "params": [
              "value"
            ],
            "type": "field"
          },
          {
            "params": [],
            "type": "mean"
          }
        ]
      ],
      "tags": []
    }
  }),
  "timeFrom": null,
  "timeShift": null,
  "title": "Panel Title",
  "tooltip": {
    "shared": true,
    "value_type": "cumulative"
  },
  "type": "graph",
  "x-axis": true,
  "y-axis": true,
  "y_formats": [
    "short",
    "short"
  ]
}
    ]
});


return dashboard;

"""
            self.cuisine.core.file_write('$tmplsDir/grafana/public/dashboards/scriptedagent.js',scriptedagent)
        if start:
            self._startGrafana(influx_addr=influx_addr, influx_port=influx_port, port=port)

    def _startGrafana(self, influx_addr='127.0.0.1', influx_port=8086,port=3000):
        cfg = self.cuisine.core.file_read('$tmplsDir/cfg/grafana/conf/defaults.ini')
        cfg = cfg.replace("http_port = 3000", "http_port = %i"%(port))
        self.cuisine.core.file_write('$cfgDir/grafana/grafana.ini', cfg)
        cmd = "$binDir/grafana-server --config=$cfgDir/grafana/grafana.ini"
        self.cuisine.process.kill("grafana-server")
        self.cuisine.processmanager.ensure("grafana-server", cmd=cmd, env={}, path="$tmplsDir/cfg/grafana/")
        grafanaclient = j.clients.grafana.get(url='http://%s:%d'%(self.cuisine.executor.addr, port),username='admin', password='admin')
        data = {
          'type': 'influxdb',
          'access': 'proxy',
          'database': 'statistics',
          'name': 'influxdb_main',
          'url': 'http://%s:%u' % (influx_addr, influx_port),
          'user': 'admin',
          'password': 'passwd',
          'default': True,
        }
        import time
        import requests
        now = time.time()
        while time.time() - now < 10:
            try:
                grafanaclient.addDataSource(data)
                if not grafanaclient.listDataSources():
                    continue
                break
            except requests.exceptions.ConnectionError:
                time.sleep(0.1)
                pass


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
        self.cuisine.core.run_script(C,profile=True)
        self.cuisine.bash.addPath("$base/bin",action=True)

    @actionrun(action=True)
    def weave(self, start=True, peer=None, jumpscalePath=True):
        if jumpscalePath:
            binPath = self.cuisine.core.joinpaths(self.cuisine.core.dir_paths['binDir'], 'weave')
        else:
            binPath = '/usr/local/bin/weave'
        self.cuisine.core.dir_ensure(j.sal.fs.getParent(binPath))

        C = '''
        curl -L git.io/weave -o {binPath} && sudo chmod a+x {binPath}
        '''.format(binPath=binPath)
        C = self.cuisine.core.args_replace(C)
        self.cuisine.package.ensure('curl')
        self.cuisine.core.run_script(C, profile=True)
        self.cuisine.bash.addPath(j.sal.fs.getParent(binPath), action=True)

        if start:
            rc, out = self.cuisine.core.run("weave status", profile=True, die=False, showout=False)
            if rc != 0:
                cmd = 'weave launch'
                if peer:
                    cmd += ' %s' % peer
                self.cuisine.core.run(cmd, profile=True)

            env = self.cuisine.core.run('weave env', profile=True)
            ss = env[len('export'):].strip().split(' ')
            for entry in ss:
                splitted = entry.split('=')
                if len(splitted) == 2:
                    self.cuisine.bash.environSet(splitted[0],splitted[1])
                elif len(splitted) > 0:
                    self.cuisine.bash.environSet(splitted[0], '')
