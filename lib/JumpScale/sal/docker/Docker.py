#!/usr/bin/env python
from Container import Container

from JumpScale import j
import os
import docker


from sal.base.SALObject import SALObject

class Docker2(SALObject):

    def __init__(self):
        self.__jslocation__ = "j.sal.docker"
        self._basepath = "/mnt/vmstor/docker"
        self._prefix = ""
        self.client = docker.Client(base_url='unix://var/run/docker.sock')
        self._containers=[]
        self._names=[]
        self.remote = {'host': 'localhost', 'port': 0}

    def connectRemoteTCP(self, address, port):
        url = '%s:%s' % (address, port)
        self.client = docker.Client(base_url=url)
        self.remote = {'host': address, 'port': port}

    def _execute(self, command):
        env = os.environ.copy()
        env.pop('PYTHONPATH', None)
        (exitcode, stdout, stderr) = j.sal.process.run(command, showOutput=False, captureOutput=True, stopOnError=False, env=env)
        if exitcode != 0:
            raise RuntimeError("Failed to execute %s: Error: %s, %s" % (command, stdout, stderr))
        return stdout


    #
    # def copy(self, name, src, dest):
    #     rndd = j.data.idgenerator.generateRandomInt(10, 1000000)
    #     temp = "/var/docker/%s/%s" % (name, rndd)
    #     j.sal.fs.createDir(temp)
    #     source_name = j.sal.fs.getBaseName(src)
    #     if j.sal.fs.isDir(src):
    #         j.do.copyTree(src, j.sal.fs.joinPaths(temp, source_name))
    #     else:
    #         j.do.copyFile(src, j.sal.fs.joinPaths(temp, source_name))
    #
    #     ddir = j.sal.fs.getDirName(dest)
    #     cmd = "mkdir -p %s" % (ddir)
    #     self.run(name, cmd)
    #
    #     cmd = "cp -r /var/jumpscale/%s/%s %s" % (rndd, source_name, dest)
    #     self.run(name, cmd)
    #     j.do.delete(temp)

    @property
    def containers(self):
        if self._containers==[]:
            for item in self.client.containers(all=all):
                name=str(item["Names"][0].strip("/").strip())
                id=str(item["Id"].strip())
                self._containers.append(Container(name, id,self.client))
        return self._containers

    @property
    def containerNamesRunning(self):
        res=[]
        for container in self.containers:
            if container.isRunning():
                res.append(container.name)
        return res

    @property
    def containerNames(self):
        res=[]
        for container in self.containers:
            res.append(container.name)
        return res

    @property
    def containersRunning(self):
        res=[]
        for container in self.containers:
            if container.isRunning():
                res.append(container)
        return res

    def exists(self,name):
        return name in self.containerNames

    @property
    def basepath(self):
        self._basepath='/mnt/data/docker'
        #@todo needs to fetch values out of hrd
        # if not self._basepath:
        #     if j.application.config.exists('docker.basepath'):
        #         self._basepath = j.application.config.get('docker.basepath')
        #     else:
        #         self._basepath="/mnt/vmstor/docker" #btrfs subvol create
        return self._basepath

    def _getChildren(self,pid,children):
        process=j.sal.process.getProcessObject(pid)
        children.append(process)
        for child in process.get_children():
            children=self._getChildren(child.pid,children)
        return children

    def _get_rootpath(self,name):
        rootpath=j.sal.fs.joinPaths(self.basepath, '%s%s' % (self._prefix, name), 'rootfs')
        return rootpath

    def _getMachinePath(self,machinename,append=""):
        if machinename=="":
            raise RuntimeError("Cannot be empty")
        base = j.sal.fs.joinPaths( self.basepath,'%s%s' % (self._prefix, machinename))
        if append!="":
            base=j.sal.fs.joinPaths(base,append)
        return base

    def status(self):
        """
        return list docker with some info

        @return list of dicts

        """
        res=[]
        for item in self.client.containers():
            name=item["Names"][0].strip(" /")
            sshport=""
            for port in item["Ports"]:
                if port["PrivatePort"]==22:
                    sshport=port["PublicPort"]
            res.append([name,item["Image"],sshport,item["Status"]])

        return res

    def ps(self):
        """
        return detailed info
        """
        return self.client.containers()

    def get(self, name, die=True):
        for container in self.containers:
            if container.name==name:
                return container
        if die:
            raise RuntimeError("Container with name %s doesn't exists" % name)
        else:
            return None

    def exportRsync(self,name,backupname,key="pub"):
        raise RuntimeError("not implemented")
        self.removeRedundantFiles(name)
        ipaddr=j.application.config.get("jssync.addr")
        path=self._getMachinePath(name)
        if not j.sal.fs.exists(path):
            raise RuntimeError("cannot find machine:%s"%path)
        if backupname[-1]!="/":
            backupname+="/"
        if path[-1]!="/":
            path+="/"
        cmd="rsync -a %s %s::upload/%s/images/%s --delete-after --modify-window=60 --compress --stats  --progress --exclude '.Trash*'"%(path,ipaddr,key,backupname)
        # print cmd
        j.sal.process.executeWithoutPipe(cmd)

    def removeRedundantFiles(self,name):
        raise RuntimeError("not implemented")
        basepath=self._getMachinePath(name)
        j.sal.fs.removeIrrelevantFiles(basepath,followSymlinks=False)

        toremove="%s/rootfs/var/cache/apt/archives/"%basepath
        j.sal.fs.removeDirTree(toremove)

    def importRsync(self,backupname,name,basename="",key="pub"):
        """
        @param basename is the name of a start of a machine locally, will be used as basis and then the source will be synced over it
        """
        raise RuntimeError("not implemented")
        ipaddr=j.application.config.get("jssync.addr")
        path=self._getMachinePath(name)

        self.btrfsSubvolNew(name)

        # j.sal.fs.createDir(path)

        if backupname[-1]!="/":
            backupname+="/"
        if path[-1]!="/":
            path+="/"

        if basename!="":
            basepath=self._getMachinePath(basename)
            if basepath[-1]!="/":
                basepath+="/"
            if not j.sal.fs.exists(basepath):
                raise RuntimeError("cannot find base machine:%s"%basepath)
            cmd="rsync -av -v %s %s --delete-after --modify-window=60 --size-only --compress --stats  --progress"%(basepath,path)
            print(cmd)
            j.sal.process.executeWithoutPipe(cmd)

        cmd="rsync -av -v %s::download/%s/images/%s %s --delete-after --modify-window=60 --compress --stats  --progress"%(ipaddr,key,backupname,path)
        print(cmd)
        j.sal.process.executeWithoutPipe(cmd)

    def exportTgz(self,name,backupname):
        raise RuntimeError("not implemented")
        self.removeRedundantFiles(name)
        path=self._getMachinePath(name)
        bpath= j.sal.fs.joinPaths(self.basepath,"backups")
        if not j.sal.fs.exists(path):
            raise RuntimeError("cannot find machine:%s"%path)
        j.sal.fs.createDir(bpath)
        bpath= j.sal.fs.joinPaths(bpath,"%s.tgz"%backupname)
        cmd="cd %s;tar Szcf %s ."%(path,bpath)
        j.sal.process.executeWithoutPipe(cmd)
        return bpath

    def importTgz(self,backupname,name):
        raise RuntimeError("not implemented")
        path=self._getMachinePath(name)
        bpath= j.sal.fs.joinPaths(self.basepath,"backups","%s.tgz"%backupname)
        if not j.sal.fs.exists(bpath):
            raise RuntimeError("cannot find import path:%s"%bpath)
        j.sal.fs.createDir(path)

        cmd="cd %s;tar xzvf %s -C ."%(path,bpath)
        j.sal.process.executeWithoutPipe(cmd)

    def create(self, name="", ports="", vols="", volsro="", stdout=True, base="jumpscale/ubuntu1510", nameserver=["8.8.8.8"],
               replace=True, cpu=None, mem=0, jumpscale=False, ssh=True, myinit=True, sharecode=False,sshkeyname="",sshpubkey="",
               setrootrndpasswd=True,rootpasswd="",jumpscalebranch="master"):

        """
        @param ports in format as follows  "22:8022 80:8080"  the first arg e.g. 22 is the port in the container
        @param vols in format as follows "/var/insidemachine:/var/inhost # /var/1:/var/1 # ..."   '#' is separator
        @param sshkeyname : use ssh-agent (can even do remote through ssh -A) and then specify key you want to use in docker
        """
        name = name.lower().strip()
        print(("create:%s" % name))

        running = [item.name for item in self.containersRunning]

        if not replace:
            if name in self.containerNamesRunning:
                j.events.opserror_critical("Cannot create machine with name %s, because it does already exists.")
        else:
            if self.exists(name):
                print("remove existing container %s" % name)
                container = self.get(name)
                if container:
                    container.destroy()

        if vols is None:
            vols = ""
        if volsro is None:
            volsro = ""
        if ports is None:
            ports = ""

        if mem is not None:
            if mem > 0:
                mem = int(mem)*1024
            elif mem <= 0:
                mem = None

        portsdict = {}
        if len(ports) > 0:
            items = ports.split(" ")
            for item in items:
                key, val = item.split(":", 1)
                portsdict[int(key)] = int(val)

        if ssh:
            if 22 not in portsdict:
                for port in range(9022, 9190):
                    if not j.sal.nettools.tcpPortConnectionTest(self.remote['host'], port):
                        portsdict[22] = port
                        print(("SSH PORT WILL BE ON:%s" % port))
                        break

        volsdict = {}
        if len(vols) > 0:
            items = vols.split("#")
            for item in items:
                key, val = item.split(":", 1)
                volsdict[str(key).strip()] = str(val).strip()

        j.sal.fs.createDir("/var/jumpscale")
        if "/var/jumpscale" not in volsdict:
            volsdict["/var/jumpscale"] = "/var/docker/%s" % name
        j.sal.fs.createDir("/var/docker/%s" % name)

        tmppath = "/tmp/dockertmp/%s" % name
        j.sal.fs.createDir(tmppath)
        volsdict[tmppath] = "/tmp"

        if sharecode and j.sal.fs.exists(path="/opt/code"):
            print("share jumpscale code")
            if "/opt/code" not in volsdict:
                volsdict["/opt/code"] = "/opt/code"

        volsdictro = {}
        if len(volsro) > 0:
            items = volsro.split("#")
            for item in items:
                key, val = item.split(":", 1)
                volsdictro[str(key).strip()] = str(val).strip()

        print("MAP:")
        for src1, dest1 in list(volsdict.items()):
            print(" %-20s %s" % (src1, dest1))

        binds = {}
        volskeys = []  # is location in docker

        for key, path in list(volsdict.items()):
            j.sal.fs.createDir(path)  # create the path on hostname
            binds[path] = {"bind": key, "ro": False}
            volskeys.append(key)

        for key, path in list(volsdictro.items()):
            j.sal.fs.createDir(path)  # create the path on hostname
            binds[path] = {"bind": key, "ro": True}
            volskeys.append(key)

        if base not in self.getImages():
            print("download docker")
            cmd = "docker pull %s" % base
            j.sal.process.executeWithoutPipe(cmd)

        if myinit:
            cmd = "sh -c \"mkdir -p /var/run/screen;chmod 777 /var/run/screen; /var/run/screen;exec >/dev/tty 2>/dev/tty </dev/tty && /sbin/my_init -- /usr/bin/screen -s bash\""
            cmd = "sh -c \" /sbin/my_init -- bash -l\""
        else:
            cmd = None

        print(("install docker with name '%s'" % name))

        if vols != "":
            print("VOLUMES")
            print(volskeys)
            print(binds)

        res = self.client.create_container(image=base, command=cmd, hostname=name, user="root", \
                detach=False, stdin_open=False, tty=True, mem_limit=mem, ports=list(portsdict.keys()), environment=None, volumes=volskeys,  \
                network_disabled=False, name=name, entrypoint=None, cpu_shares=cpu, working_dir=None, domainname=None, memswap_limit=None)

        if res["Warnings"] is not None:
            raise RuntimeError("Could not create docker, res:'%s'" % res)

        id = res["Id"]

        res = self.client.start(container=id, binds=binds, port_bindings=portsdict, lxc_conf=None, \
            publish_all_ports=False, links=None, privileged=False, dns=nameserver, dns_search=None, volumes_from=None, network_mode=None)

        container = Container(name,id, self.client, self.remote['host'])

        if ssh:
            # time.sleep(0.5)  # give time to docker to start
            container.pushSSHKey(keyname=sshkeyname, sshpubkey=sshpubkey)

            if jumpscale:
                container.installJumpscale(jumpscalebranch)

            if setrootrndpasswd:
                if rootpasswd is None or rootpasswd == '':
                    print("set default root passwd (gig1234)")
                    container.executor.execute("echo \"root:gig1234\"|chpasswd",showout=False)
                else:
                    print("set root passwd to %s" % rootpasswd)
                    container.cexecutor.execute("echo \"root:%s\"|chpasswd" % rootpasswd,showout=False)

            container.setHostName(name)
        return container




    def getImages(self):
        images=[str(item["RepoTags"][0]).replace(":latest","") for item in self.client.images()]
        return images

    def removeImages(self,tag="<none>:<none>"):
        for item in self.client.images():
            if tag in item["RepoTags"]:
                self.client.remove_image(item["Id"])

    def destroyAll(self):
        for container in self.containers:
            container.destroy()

    def resetDocker(self):
        self.destroyContainers()

        rc,out=j.sal.process.execute("mount")
        mountpoints=[]
        for line in out.split("\n"):
            if line.find("type btrfs")!=-1:
                mountpoint=line.split("on ")[1].split("type")[0].strip()
                mountpoints.append(mountpoint)

        for mountpoint in mountpoints:
            j.sal.btrfs.subvolumesDelete(mountpoint,"/docker/")

        j.do.execute("apt-get remove docker-engine -y")
        j.do.execute("rm -rf /var/lib/docker")
        j.do.execute("apt-get install docker-engine -y")


    def pull(self,imagename):
        cmd="docker pull %s"%imagename
        j.sal.process.executeWithoutPipe(cmd)
