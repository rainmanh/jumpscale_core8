from JumpScale import j
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import time


class MyFSEventHandler(FileSystemEventHandler):

    def catch_all_handler(self, event):
        if event.is_directory:
            return
            # j.tools.debug.syncCode()
        else:
            changedfile = event.src_path
            for node in j.tools.debug.nodes:
                sep = "jumpscale_core8/lib/JumpScale/"
                sep_cmds = "jumpscale_core8/shellcmds/"
                if changedfile.find(sep) != -1:
                    dest0 = changedfile.split(sep)[1]
                    dest = "/optrw/jumpscale8/lib/JumpScale/%s" % (dest0)
                elif changedfile.find(sep_cmds) != -1:
                    dest0 = changedfile.split(sep_cmds)[1]
                    dest = "/optrw/jumpscale8/bin/%s" % (dest0)
                elif changedfile.find("/.git/") != -1:
                    return
                elif changedfile.find("/__pycache__/") != -1:
                    return
                elif j.do.getBaseName(changedfile) in ["InstallTools.py", "ExtraTools.py"]:
                    base = j.do.getBaseName(changedfile)
                    dest = "/optrw/jumpscale8/lib/JumpScale/%s" % (base)
                else:
                    destpart = changedfile.split("jumpscale/", 1)[-1]
                    dest = "/optrw/code/%s" % destpart

                print("copy: %s %s:%s" % (changedfile, node, dest))
                try:
                    node.ftpclient.put(changedfile, dest)
                except Exception as e:
                    print(e)
                    j.tools.debug.syncCode()
                    

    def on_moved(self, event):
        self.catch_all_handler(event)

    def on_created(self, event):
        self.catch_all_handler(event)

    def on_deleted(self, event):
        self.catch_all_handler(event)

    def on_modified(self, event):
        self.catch_all_handler(event)



class DebugSSHNode():

    def __init__(self, addr="localhost", sshport=22):
        self.addr = addr
        self.port = sshport

        #lets test tcp on 22 if not then 9022 which are our defaults
        test=j.sal.nettools.tcpPortConnectionTest(self.addr,self.port,2)
        if test==False:
            if self.port==22:
                test= j.sal.nettools.tcpPortConnectionTest(self.addr,9022,1)
                if test:
                    self.port=9022
        if test==False:
            raise RuntimeError("Cannot connect to %s:%s"%(self.addr,self.port))

        self._platformType = None
        self._sshclient = None
        self._ftpclient = None

    @property
    def ftpclient(self):
        if self._ftpclient == None:
            self._ftpclient = self.sshclient.getSFTP()
        return self._ftpclient

    @property
    def executor(self):
        return self.cuisine.executor

    @property
    def cuisine(self):
        if self.port == 0:
            return j.tools.cuisine.local
        else:
            return self.sshclient.cuisine

    @property
    def sshclient(self):
        if self._sshclient == None:
            if self.port != 0:
                self._sshclient = j.clients.ssh.get(self.addr, port=self.port)
            else:
                return None
        return self._sshclient

    @property
    def platformType(self):
        if self._platformType != None:
            from IPython import embed
            print("platformtype")
            embed()
        return self._platformType



    def __str__(self):
        return "debugnode:%s" % self.addr

    __repr__ = __str__


class DevelopToolsFactory():

    def __init__(self):
        self.__jslocation__ = "j.tools.develop"
        self._nodes = []
        self.installer=Installer()

    def help(self):
        H = """
        example to use #@todo change python3... to js... (but not working on osx yet)
        js 'j.tools.debug.init("ovh4,ovh3")'
        js 'j.tools.debug.installJSSandbox(rw=True)' #will install overlay sandbox wich can be editted
        js 'j.tools.debug.syncCode(True)'
        if you now go onto e.g. ovh4 you will see on /optrw/... all changes reflected which you make locally

        example output:
        ```
        Make a selection please:
           1: /Users/despiegk/opt/code/github/jumpscale/ays_jumpscale8
           2: /Users/despiegk/opt/code/github/jumpscale/dockers
           3: /Users/despiegk/opt/code/github/jumpscale/docs8
           4: /Users/despiegk/opt/code/github/jumpscale/gig_it_ays
           5: /Users/despiegk/opt/code/github/jumpscale/jumpscale_core8
           6: /Users/despiegk/opt/code/github/jumpscale/play7
           7: /Users/despiegk/opt/code/github/jumpscale/play8

        Select Nr, use comma separation if more e.g. "1,4", * is all, 0 is None: 2,5

        rsync  -rlptgo --partial --exclude '*.egg-info*/' --exclude '*.dist-info*/' --exclude '*__pycache__*/' --exclude '*.git*/' --exclude '*.egg-info*' --exclude '*.pyc' --exclude '*.bak' --exclude '*__pycache__*'  -e 'ssh -o StrictHostKeyChecking=no -p 22' '/Users/despiegk/opt/code/github/jumpscale/dockers/' 'root@ovh4:/optrw/code/dockers/'
        ... some more rsync commands

        monitor:/Users/despiegk/opt/code/github/jumpscale/dockers
        monitor:/Users/despiegk/opt/code/github/jumpscale/jumpscale_core8

        #if you change a file:

        copy: /Users/despiegk/opt/code/github/jumpscale/jumpscale_core8/lib/JumpScale/tools/debug/Debug.py debugnode:ovh4:/optrw/jumpscale8/lib/JumpScale/tools/debug/Debug.py

        ```

        """
        print (H)

    def init(self, nodes="localhost"):
        """
        define which nodes to init,
        format="localhost,ovh4,anode:2222,192.168.6.5:23"
        this will be remembered in local redis for further usage
        """
        self._nodes=[]
        j.core.db.set("debug.nodes", nodes)

    @property
    def nodes(self):
        if self._nodes == []:
            if j.core.db.get("debug.nodes") == None:
                self.init()
            nodes = j.core.db.get("debug.nodes").decode()

            for item in nodes.split(","):
                if item.find(":") != -1:
                    addr, sshport = item.split(":")
                    addr = addr.strip()
                    sshport = int(sshport)                    

                else:
                    addr = item.strip()
                    if addr != "localhost":
                        sshport = 22
                    else:
                        sshport = 0
                self._nodes.append(DebugSSHNode(addr, sshport))
        return self._nodes

    def installJSSandbox(self, rw=False,resetstate=False):
        """
        install jumpscale, will be done as sandbox over fuse layer for linux
        otherwise will try to install jumpscale inside OS

        @input rw, if True will put overlay filesystem on top of /opt -> /optrw which will allow you to manipulate/debug the install
        @input synclocalcode, sync the local github code to the node (jumpscale) (only when in rw mode)
        @input reset, remove old code (only used when rw mode)
        @input monitor detect local changes & sync (only used when rw mode)
        """

        if resetstate:
            j.actions.reset("develop")

        def cleanNode(node):
            """
            make node clean e.g. remove redis, install tmux, stop js8, unmount js8
            """
            C = """
            set +ex
            pskill redis-server #will now kill too many redis'es, should only kill the one not in docker
            pskill redis #will now kill too many redis'es, should only kill the one not in docker
            umount -fl /optrw
            apt-get remove redis-server -y
            rm -rf /overlay/js_upper
            rm -rf /overlay/js_work
            rm -rf /optrw
            js8 stop
            pskill js8
            umount -f /opt
            apt-get install tmux fuse -y
            """
            node.cuisine.run_script(C)

        def installJS8SB(node,rw=False):
            """
            install jumpscale8 sandbox in read or readwrite mode
            """
            C = """
            set -ex
            cd /usr/bin
            rm -f js8
            wget http://stor.jumpscale.org/ays/bin/js8
            chmod +x js8
            cd /
            mkdir -p /opt

            js8
            """
            node.cuisine.run_script(C)            

        for node in self.nodes:
            j.actions.add(cleanNode, args={"node":node},retry=2,runid="develop")
            j.actions.add(installJS8SB, args={"node":node,"rw":rw},retry=2,runid="develop")
            
        if rw:
            self.overlaySandbox()

    def resetState(self):
        j.actions.reset("develop")

    def overlaySandbox(self):

        def overlaySandbox(node):
            """
            create overlay on top of sandbox
            """        
            C = """
            set -ex
            mkdir -p /overlay/js_upper
            mkdir -p /overlay/js_work
            mkdir -p /optrw
            mount -t overlay overlay -o lowerdir=/opt,upperdir=/overlay/js_upper,workdir=/overlay/js_work /optrw
            set +ex
            rm -rf /optrw/jumpscale8/lib/JumpScale/
            mkdir -p /optrw/jumpscale8/lib/JumpScale/
            mkdir -p /optrw/code/
            """
            node.cuisine.run_script(C)   
    


        def overlaySandboxSetEnv(node):
            """
            make sure new env arguments are understood on platform
            """
            NEWENV="""
            export JSBASE=/optrw/jumpscale8

            export PATH=$JSBASE/bin:$PATH
            export PYTHONHOME=$JSBASE/bin


            export PYTHONPATH=.:$JSBASE/lib:$JSBASE/lib/lib-dynload/:$JSBASE/bin:$JSBASE/lib/python.zip:$JSBASE/lib/plat-x86_64-linux-gnu
            export LD_LIBRARY_PATH=$JSBASE/bin
            export PS1="JS8: "
            if [ -n "$BASH" -o -n "$ZSH_VERSION" ] ; then
                    hash -r 2>/dev/null
            fi

            """
            node.cuisine.file_write("/optrw/jumpscale8/env.sh", NEWENV,check=True)

        for node in self.nodes:
            j.actions.add(overlaySandbox, args={"node":node},retry=2,runid="develop")
            j.actions.add(overlaySandboxSetEnv, args={"node":node},retry=2,runid="develop")

        print ("\nlogin to machine & do\ncd /optrw/jumpscale8;source env.sh;js")

    def syncCode(self, reset=False, ask=False,monitor=False,rsyncdelete=False):
        """
        sync all code to the remote destinations

        @param reset=True, means we remove the destination first
        @param ask=True means ask which repo's to sync (will get remembered in redis)

        """
        if ask or j.core.db.get("debug.codepaths") == None:
            path = j.dirs.codeDir + "/github/jumpscale"
            if j.do.exists(path):
                items = j.do.listDirsInDir(path)
            chosen = j.tools.console.askChoiceMultiple(items)
            j.core.db.set("debug.codepaths", ",".join(chosen))


        if reset:
            self.overlaySandbox()

        codepaths = j.core.db.get("debug.codepaths").decode().split(",")
        for source in codepaths:
            destpart = source.split("jumpscale/", 1)[-1]
            for node in self.nodes:
                if node.port != 0:
                    dest = "root@%s:/optrw/code/%s" % (node.addr, destpart)

                    if destpart == "jumpscale_core8":
                        dest = "root@%s:/optrw/jumpscale8/lib/JumpScale/" % node.addr
                        source2 = source + "/lib/JumpScale/"
                        j.do.copyTree(source2, dest, ignoredir=['.egg-info', '.dist-info', '__pycache__', ".git"], rsync=True, ssh=True, sshport=node.port, recursive=True,rsyncdelete=rsyncdelete)

                        source2 = source + "/install/InstallTools.py"
                        dest = "root@%s:/optrw/jumpscale8/lib/JumpScale/InstallTools.py" % node.addr
                        j.do.copyTree(source2, dest, ignoredir=['.egg-info', '.dist-info', '__pycache__', ".git"], rsync=True, ssh=True, sshport=node.port, recursive=False)

                        source2 = source + "/install/ExtraTools.py"
                        dest = "root@%s:/optrw/jumpscale8/lib/JumpScale/ExtraTools.py" % node.addr
                        j.do.copyTree(source2, dest, ignoredir=['.egg-info', '.dist-info', '__pycache__', ".git"], rsync=True, ssh=True, sshport=node.port, recursive=False)

                    else:
                        node.cuisine.run("mkdir -p /optrw/code/%s" % destpart)
                        j.do.copyTree(source, dest, ignoredir=['.egg-info', '.dist-info', '__pycache__', ".git"], rsync=True, ssh=True, sshport=node.port, recursive=True,rsyncdelete=rsyncdelete)
                else:
                    # symlink into codetree
                    import ipdb
                    ipdb.set_trace()
        if monitor:
            self.monitorChanges()

    def monitorChanges(self,sync=True,reset=False):
        """
        look for changes in directories which are being pushed & if found push to remote nodes
        """
        event_handler = MyFSEventHandler()
        observer = Observer()
        if sync or j.core.db.get("debug.codepaths") == None:
            self.syncCode(monitor=False,rsyncdelete=False,reset=reset)
        codepaths = j.core.db.get("debug.codepaths").decode().split(",")
        for source in codepaths:
            print("monitor:%s" % source)
            observer.schedule(event_handler, source, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass


class Installer():

    def installAgentcontroller(self,start=True):
        """
        config: https://github.com/Jumpscale/agent2/wiki/agent-configuration
        """
        j.actions.setRunId("installAgentController")

        agentAppDir = j.do.joinPaths(j.dirs.base, "apps", "agent8")
        agentcontrollerAppDir = j.do.joinPaths(j.dirs.base, "apps", "agentcontroller8")
        syncthingAppDir = j.do.joinPaths(j.dirs.base, "apps", "syncthing")

        def upgradePip():
            print("upgrading pip")
            j.do.execute("pip3 install --upgrade pip")

        def pythonLibInstall():
            print('installing pytoml')
            j.do.execute("pip3 install pytoml")

        def agent_get(agentdir, syncthingdir):
            url = "git@git.aydo.com:binary/agent2.git"
            dest = j.do.pullGitRepo(url)

            j.do.createDir(agentdir)
            j.do.createDir(syncthingdir)
            j.sal.fs.symlink(j.sal.fs.joinPaths(dest, 'extensions', 'syncthing', 'syncthing'), j.sal.fs.joinPaths(syncthingdir, 'syncthing'), overwriteTarget=True)
            j.sal.fs.symlink(j.sal.fs.joinPaths(dest, 'agent2'), j.sal.fs.joinPaths(agentdir, 'agent2'), overwriteTarget=True)
            j.sal.fs.copyFile(j.sal.fs.joinPaths(dest, 'agent2.toml'), agentdir)

            # link extensions
            extdir = j.sal.fs.joinPaths(dest, "extensions")
            j.sal.fs.symlink(extdir, j.sal.fs.joinPaths(agentdir, 'extensions'), overwriteTarget=True)

            # link conf
            j.sal.fs.symlink(j.sal.fs.joinPaths(dest, "conf"), j.sal.fs.joinPaths(agentdir, 'conf'), overwriteTarget=True)

        def agentcontroller_get(appbase):
            url = "git@git.aydo.com:binary/agentcontroller2.git"
            dest = j.do.pullGitRepo(url)

            j.do.createDir(appbase)
            j.sal.fs.symlink(j.do.joinPaths(dest, "agentcontroller2", "agentcontroller2"), j.sal.fs.joinPaths(appbase, "agentcontroller2"), overwriteTarget=True)
            j.sal.fs.copyFile(j.do.joinPaths(dest, "agentcontroller2", "agentcontroller2.toml"), appbase)

            extdir = j.sal.fs.joinPaths(appbase, "extensions")
            j.sal.fs.createDir(extdir)
            j.sal.fs.symlink(j.sal.fs.joinPaths(dest, 'extensions'), extdir, overwriteTarget=True)

        j.actions.add(upgradePip)
        j.actions.add(pythonLibInstall)
        j.actions.add(agent_get, args={"agentdir": agentAppDir, 'syncthingdir': syncthingAppDir})
        j.actions.add(agentcontroller_get, args={"appbase": agentcontrollerAppDir})
        j.actions.run()

        def startSyncthing(appbase):
            j.sal.tmux.executeInScreen("main", screenname="syncthing",cmd="./syncthing -gui-address 127.0.0.1:18384", wait=0, cwd=appbase, env=None, user='root', tmuxuser=None)

        def startAgent(appbase):
            j.sal.tmux.executeInScreen("main", screenname="agent",cmd="./agent2 -c agent2.toml", wait=0, cwd=appbase, env=None, user='root', tmuxuser=None)

        def startAgentController(appbase):
            j.sal.tmux.executeInScreen("main", screenname="ac",cmd="./agentcontroller2 -c agentcontroller2.toml", wait=0,
                                       cwd=appbase, env=None, user='root', tmuxuser=None)

        if start:
            j.actions.add(startSyncthing, args={"appbase": syncthingAppDir})
            j.actions.add(startAgentController, args={"appbase": agentcontrollerAppDir})
            j.actions.add(startAgent, args={"appbase": agentAppDir})
            j.actions.run()
        else:
            print('To run your agent/agentcontroller, navigate to "%s" adn to "%s" and do "..."' % agentAppDir)


    def installPortal(self, start=True,mongodbip="127.0.0.1",mongoport=27017,login="",passwd=""):

        j.actions.setRunId("installportal")

        def upgradePip():
            j.do.execute("pip3 install --upgrade pip")
        actionUpgradePIP=j.actions.add(upgradePip)

        def installDeps(actionin):
            """
            make sure new env arguments are understood on platform
            """
            deps="""
            setuptools
            aioredis
            # argh
            bcrypt
            Beaker
            blinker
            blosc
            # Cerberus
            # certifi
            # cffi
            # click
            # credis
            # crontab
            # Cython
            decorator
            # docker-py
            # dominate
            # ecdsa
            Eve
            Eve-docs
            Eve-Mongoengine
            # Events
            # Flask
            # Flask-Bootstrap
            # Flask-PyMongo
            gevent==1.1rc2
            # gitdb
            gitlab3
            # GitPython
            greenlet
            # hiredis
            html2text
            # influxdb
            # ipdb
            # ipython
            # ipython-genutils
            itsdangerous
            Jinja2
            # marisa-trie
            MarkupSafe
            mimeparse
            mongoengine
            msgpack-python
            netaddr
            # paramiko
            # path.py
            pathtools
            # pexpect
            # pickleshare
            psutil
            # psycopg2
            # ptyprocess
            # pycparser
            # pycrypto
            pycurl
            # pygo
            # pygobject
            pylzma
            pymongo
            pystache
            # python-apt
            python-dateutil
            pytoml
            pytz
            PyYAML
            # pyzmq
            # redis
            # reparted
            requests
            simplegeneric
            simplejson
            six
            # smmap
            # SQLAlchemy
            traitlets
            ujson
            # unattended-upgrades
            urllib3
            visitor
            # watchdog
            websocket
            websocket-client
            Werkzeug
            wheel
            # zmq
            """


            def installPip(name):
                j.do.execute("pip3 install %s --upgrade"%name)
            
            actionout=None
            for dep in deps.split("\n"):
                dep=dep.strip()
                if dep.strip()=="":
                    continue
                if dep.strip()[0]=="#":
                    continue
                dep=dep.split("=",1)[0]
                actionout=j.actions.add(installPip, args={"name":dep},retry=2,deps=[actionin])

            return actionout
        actiondeps=installDeps(actionUpgradePIP)

        def getcode():
            j.do.pullGitRepo("git@github.com:Jumpscale/jumpscale_portal8.git")
        actionGetcode=j.actions.add(getcode,deps=[])


        def install():
            destjslib = j.do.getPythonLibSystem(jumpscale=True)
            j.do.symlink("%s/github/jumpscale/jumpscale_portal8/lib/portal" % j.do.CODEDIR, "%s/portal" % destjslib, delete=False)
            j.do.symlink("%s/github/jumpscale/jumpscale_portal8/lib/portal" % j.do.CODEDIR, "%s/portal" % j.dirs.jsLibDir, delete=False)
            
            # j.application.reload()

            portaldir = '%s/apps/portals/' % j.do.BASE
            exampleportaldir = '%sexample' % portaldir
            j.do.createDir(exampleportaldir)
            j.do.symlink("%s/github/jumpscale/jumpscale_portal8/jslib" % j.do.CODEDIR, '%s/jslib' % portaldir)
            j.do.symlink("%s/github/jumpscale/jumpscale_portal8/apps/portalbase" % j.do.CODEDIR,  '%s/portalbase' % portaldir)
            j.do.createDir('%s/base/home/.space' % exampleportaldir)
            j.do.copyFile("%s/portalbase/portal_no_ays.py" % portaldir, exampleportaldir)
            j.do.copyFile("%s/portalbase/config.hrd" % portaldir, exampleportaldir)
            j.dirs.replaceFilesDirVars("%s/config.hrd"%exampleportaldir)
            j.do.copyTree("%s/jslib/old/images" % portaldir, "%s/jslib/old/elfinder" % portaldir)
        actioninstall=j.actions.add(install,deps=[actiondeps])

        def changeEve():
            #2to3 -f all -w /usr/local/lib/python3.5/site-packages/eve_docs/config.py
            #@todo
            pass
        action=j.actions.add(changeEve,deps=[actionGetcode,actioninstall])

        def startmethod():
            #@tod needs to become tmux
            portaldir = '%s/apps/portals/' % j.do.BASE
            exampleportaldir = '%sexample' % portaldir
            cmd="cd %s; jspython portal_no_ays.py" % exampleportaldir
            j.sal.tmux.executeInScreen("portal", "portal", cmd, wait=0, cwd=None, env=None, user='root', tmuxuser=None)
            # j.do.execute()
        if start:
            actionstart=j.actions.add(startmethod)            
        else:
            print('To run your portal, navigate to "%s" and do "jspython portal_no_ays.py"' % exampleportaldir)


        j.actions.run()

        #cd /usr/local/Cellar/mongodb/3.2.1/bin/;./mongod --dbpath /Users/kristofdespiegeleer1/optvar/mongodb


        #@todo install gridportal as well
        #@link example spaces
        #@eve issue
        #@explorer issue



    def installArchLinuxToSDCard(self,executor=None,redownload=False):
        """
        will only work if 1 sd card found of 8 or 16 GB, be careful will overwrite the card   
        executor = a linux machine     

        executor=j.tools.executor.getSSHBased(addr="192.168.0.23", port=22,login="root",passwd="rooter",pushkey="ovh_install")
        j.tools.develop.installer.installArchLinuxToSDCard(executor)

        """

        executor=j.tools.executor.get(executor)

        j.actions.setRunId("installArchSD")

        def partition(executor):
            def findDevice(executor):
                devs=[]
                for line in executor.cuisine.run("lsblk -b -o TYPE,NAME,SIZE").split("\n"):
                    if line.startswith("disk"):
                        while line.find("  ")>0:
                            line=line.replace("  "," ")
                        ttype,dev,size=line.split(" ")
                        size=int(size)
                        if size>15000000000 and size < 17000000000:
                            devs.append(dev)
                        if size>7500000000 and size < 8500000000:
                            devs.append(dev)
                if len(devs)!=1:
                    raise RuntimeError("could not find flash disk device, found %s (need to find 1 of 8 or 16 GB size)"%devs)
                return dev


            dev=findDevice(executor)

            cmd="parted -s /dev/%s mklabel msdos mkpar primary fat32 2 100M mkpart primary ext4 100M 100"%dev
            cmd+="%"
            executor.cuisine.run(cmd)


        j.actions.add(partition)

        def 
        'nmap -p22 --open -PN -sV -oG ssh_hosts 192.168.88.0/24'

        S="""
        cd /root
        pacman -S git
        go git https://github.com/oblique/create_ap'
        pacman -S hostapd
        pacman -S haveged
        pacman -S util-linux
        pacman -S dnsmasq
        pacman -S iw
        pacman -S iwconfig
# 
        for item in self.cuisine.fs_find("/mnt/pub",extendinfo=True):
            path,sizeinkb,epochmod=item
            from IPython import embed
            print ("DEBUG NOW sdsd")
            embed()
            p
            
        """