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
            changedfile=event.src_path
            for  node in  j.tools.debug.nodes:
                sep="jumpscale_core8/lib/JumpScale/"
                if changedfile.find(sep)!=-1:
                    dest0=changedfile.split(sep)[1]
                    dest="root@%s:/optrw/jumpscale8/lib/JumpScale/%s"%(node.addr,dest0)
                    dest="/optrw/jumpscale8/lib/JumpScale/%s"%(dest0)
                elif changedfile.find("/.git/")!=-1:
                    return
                elif changedfile.find("/__pycache__/")!=-1:
                    return
                elif j.do.getBaseName(changedfile) in ["InstallTools.py","ExtraTools.py"]:
                    base=j.do.getBaseName(changedfile)
                    dest="/optrw/jumpscale8/lib/JumpScale/%s"%(base)
                else:
                    destpart=changedfile.split("jumpscale/",1)[-1]
                    dest="/optrw/code/%s"%destpart

                print ("copy: %s %s:%s"%(changedfile,node,dest))
                node.ftpclient.put(changedfile, dest)

                

    def on_moved(self, event):
        self.catch_all_handler(event)

    def on_created(self, event):
        self.catch_all_handler(event)

    def on_deleted(self, event):
        self.catch_all_handler(event)

    def on_modified(self, event):
        self.catch_all_handler(event)


class DebugSSHNode():

    def __init__(self,addr="localhost",sshport=22):
        self.addr=addr
        self.port=sshport
        self._platformType=None
        self._sshclient=None
        self._ftpclient=None

    @property
    def ftpclient(self):
        if self._ftpclient==None:
            self._ftpclient=self.sshclient.getSFTP()
        return self._ftpclient
    

    @property
    def executor(self):
        return self.cuisine.executor

    @property
    def cuisine(self):
        if self.port==0:
            return j.tools.cuisine.local
        else:
            return self.sshclient.cuisine

    @property
    def sshclient(self):
        if self._sshclient==None:
            if self.port!=0:
                self._sshclient=j.clients.ssh.get(self.addr, port=self.port)
            else:
                return None
        return self._sshclient

    @property
    def platformType(self):
        if self._platformType!=None:
            from IPython import embed
            print ("platformtype")
            embed()
        return self._platformType

    def __str__(self):
        return "debugnode:%s"%self.addr

    __repr__=__str__
        


class DebugFactory():

    def __init__(self):
        self.__jslocation__ = "j.tools.debug"
        self._nodes=[]

    def help():
        H="""
        example to use
        python3 -c 'from JumpScale import j;j.tools.debug.init("ovh4,ovh3")'
        python3 -c 'from JumpScale import j;j.tools.debug.installJSSandbox(rw=True)' #will install overlay sandbox wich can be editted
        python3 -c 'from JumpScale import j;j.tools.debug.syncCode(True)'
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

    def init(self,nodes="localhost"):
        """
        define which nodes to init, 
        format="localhost,ovh4,anode:2222,192.168.6.5:23"
        this will be remembered in local redis for further usage
        """
        j.core.db.set("debug.nodes",nodes)

    @property
    def nodes(self):
        if self._nodes==[]:
            if j.core.db.get("debug.nodes")==None:
                self.init()
            nodes=j.core.db.get("debug.nodes").decode()

            for item in nodes.split(","):
                if item.find(":")!=-1:
                    addr,sshport=item.split(":")
                    addr=addr.strip()
                    sshport=int(sshport)
                else:
                    addr=item.strip()
                    if addr!="localhost":
                        sshport=22
                    else:
                        sshport=0
                self._nodes.append(DebugSSHNode(addr,sshport))
        return self._nodes

    def installJSSandbox(self,rw=False,synclocalcode=False):
        """
        install jumpscale, will be done as sandbox over fuse layer for linux
        otherwise will try to install jumpscale inside OS

        @input rw, if True will put overlay filesystem on top of /opt -> /optrw which will allow you to manipulate/debug the install
        """
        C="""
        set +ex
        pskill redis-server #will now kill too many redis'es, should only kill the one not in docker
        pskill redis #will now kill too many redis'es, should only kill the one not in docker
        umount -f /optrw
        js8 stop
        pskill js8
        umount -f /opt
        set -ex
        apt-get install tmux fuse -y
        cd /usr/bin
        rm -f js8
        wget http://stor.jumpscale.org/ays/bin/js8
        chmod +x js8
        cd /
        mkdir -p /opt
        js8
        """

        for node in self.nodes:
            node.cuisine.run_script(C)
        if rw:
            self.overlaySandox()

        if synclocalcode:
            self.syncCode()

    def overlaySandox(self):
        C="""
        set +ex
        umount -f /optrw
        rm -rf /overlay/js_upper
        rm -rf /overlay/js_work
        rm -rf /optrw
        set -ex
        mkdir -p /overlay/js_upper
        mkdir -p /overlay/js_work
        mkdir -p /optrw
        mount -t overlay overlay -olowerdir=/opt,upperdir=/overlay/js_upper,workdir=/overlay/js_work /optrw
        mkdir -p /optrw/jumpscale8/lib/JumpScale/
        mkdir -p /optrw/code/
        """
        for node in self.nodes:
            node.cuisine.run_script(C)
              
    def syncCode(self,reset=False,monitor=True):
        if reset or j.core.db.get("debug.codepaths")==None:
            path=j.dirs.codeDir+"/github/jumpscale"
            if j.do.exists(path):
                items=j.do.listDirsInDir(path)
            chosen=j.tools.console.askChoiceMultiple(items)
            j.core.db.set("debug.codepaths",",".join(chosen))
        codepaths=j.core.db.get("debug.codepaths").decode().split(",")
        for source in codepaths:
            destpart=source.split("jumpscale/",1)[-1]
            for node in self.nodes:
                if node.port!=0:
                    dest="root@%s:/optrw/code/%s"%(node.addr,destpart)
                    
                    if destpart=="jumpscale_core8":
                        dest="root@%s:/optrw/jumpscale8/lib/JumpScale/"%node.addr
                        source2=source+"/lib/JumpScale/"
                        j.do.copyTree(source2, dest, ignoredir=['.egg-info', '.dist-info','__pycache__',".git"], rsync=True, ssh=True, sshport=node.port, recursive=True)
                        
                        source2=source+"/install/InstallTools.py"
                        dest="root@%s:/optrw/jumpscale8/lib/JumpScale/InstallTools.py"%node.addr
                        j.do.copyTree(source2, dest, ignoredir=['.egg-info', '.dist-info','__pycache__',".git"], rsync=True, ssh=True, sshport=node.port, recursive=False)

                        source2=source+"/install/ExtraTools.py"
                        dest="root@%s:/optrw/jumpscale8/lib/JumpScale/ExtraTools.py"%node.addr
                        j.do.copyTree(source2, dest, ignoredir=['.egg-info', '.dist-info','__pycache__',".git"], rsync=True, ssh=True, sshport=node.port, recursive=False)

                    else:
                        node.ftpclient.mkdir("/optrw/code/%s"%destpart)
                        j.do.copyTree(source, dest, ignoredir=['.egg-info', '.dist-info','__pycache__',".git"], rsync=True, ssh=True, sshport=node.port, recursive=True)
                else:
                    #symlink into codetree
                    import ipdb
                    ipdb.set_trace()
        if monitor:
            self.monitorChanges()

    def monitorChanges(self):
        """
        look for changes in directories which are being pushed & if found push to remote nodes
        """
        event_handler=MyFSEventHandler()                    
        observer = Observer()
        codepaths=j.core.db.get("debug.codepaths").decode().split(",")
        for source in codepaths:
            print ("monitor:%s"%source)
            observer.schedule(event_handler, source, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
                pass



