
from JumpScale import j
import os

import socket

from ActionDecorator import ActionDecorator
class actionrun(ActionDecorator):
    def __init__(self,*args,**kwargs):
        ActionDecorator.__init__(self,*args,**kwargs)
        self.selfobjCode="cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.installer"


class CuisineInstaller(object):

    def __init__(self,executor,cuisine):
        self.executor=executor
        self.cuisine=cuisine

    @actionrun(action=True)
    def redis(self):
        defport=6379
        if self.cuisine.process_tcpport_check(defport,"redis"):
            print ("no need to install, already there & running")
            return

        if self.cuisine.isUbuntu:
            package="redis-server"
        else:
            package="redis"

        self.cuisine.package.install(package)
        self.cuisine.package.start(package)

        if self.cuisine.process_tcpport_check(defport,"redis")==False:
            raise RuntimeError("Could not install redis, port was not running")

    @actionrun(action=True)
    def sshreflector_server(self,reset=False):
        """
        to test
        js 'c=j.tools.cuisine.get("stor1:9022");c.installer.sshreflector()'
        """

        port=9222

        package="dropbear"
        self.cuisine.package.install(package)

        self.cuisine.run("rm -f /etc/default/dropbear",die=False)
        self.cuisine.run("killall dropbear",die=False   )

        passwd=j.data.idgenerator.generateGUID()
        self.cuisine.user_ensure("sshreflector", passwd=passwd, home="/home/sshreflector", uid=None, gid=None, shell=None, fullname=None, encrypted_passwd=True, group=None)

        self.cuisine.run('ufw allow %s'%port,die=False)

        self.cuisine.dir_ensure("/home/sshreflector/.ssh", recursive=True, mode=None, owner="sshreflector", group="sshreflector")

        lpath=os.environ["HOME"]+"/.ssh/reflector"
        path="/home/sshreflector/.ssh/reflector"
        ftp=self.cuisine.executor.sshclient.getSFTP()
        if j.do.exists(lpath):
            print("UPLOAD EXISTING SSH KEYS")
            ftp.put(lpath,path)
            ftp.put(lpath+".pub",path+".pub")
        else:
            if reset:
                self.cuisine.file_unlink(path)
            if not self.cuisine.file_exists(path):
                self.cuisine.run("ssh-keygen -f %s -N ''"%path)

            ftp.get(path,lpath)
            ftp.get(path+".pub",lpath+".pub")

            j.do.chmod(lpath,0o600)
            j.do.chmod(lpath+".pub",0o600)

        #authorize remote server to accept now copied private key
        self.cuisine.ssh_authorize("sshreflector",j.do.readFile(lpath+".pub"))

        self.cuisine.run("chmod 0644 /home/sshreflector/.ssh/*")
        self.cuisine.run("chown -R sshreflector:sshreflector /home/sshreflector/.ssh/")

        cpath=self.cuisine.run("which dropbear")

        cmd="%s -R -F -E -p 9222 -w -s -g -K 20 -I 60"%cpath
        self.cuisine.systemd_ensure("reflector", cmd, descr='')

        # self.cuisine.package.start(package)

        self.cuisine.hostfile_set_fromlocal()

        if self.cuisine.process_tcpport_check(port,"dropbear")==False:
            raise RuntimeError("Could not install dropbear, port %s was not running"%port)

    @actionrun()
    def sshreflector_createconnection(self,remoteids):
        """
        @param remoteids are the id's of the reflectors e.g. 'ovh3,ovh5:3333'
        """
        self.cuisine.run("killall autossh",die=False)
        self.cuisine.package.install("autossh")


        if remoteids.find(",")!=-1:
            cuisine=None
            for item in remoteids.split(","):
                try:
                    cuisine=j.tools.cuisine.get(item)
                except:
                    pass
        else:
            cuisine=j.tools.cuisine.get(remoteids)
        if cuisine==None:
            raise RuntimeError("could not find reflector active")

        rpath="/home/sshreflector/reflectorclients"
        lpath=os.environ["HOME"]+"/.ssh/reflectorclients"
        ftp=cuisine.executor.sshclient.getSFTP()
        ftp.get(rpath,lpath)

        out=self.cuisine.file_read(lpath)

        addr=cuisine.executor.addr

        keypath=os.environ["HOME"]+"/.ssh/reflector"

        for line in out.split("\n"):
            if line.strip()=="":
                continue
            name,port=line.split(":")

            # cmd="ssh sshreflector@%s -o StrictHostKeyChecking=no -p 9222 -i %s -L %s:localhost:%s"%(addr,keypath,port,port)
            # self.cuisine.tmux.executeInScreen("ssh",name,cmd)

            cmd="autossh -M 0 -N -f -o ExitOnForwardFailure=yes -o \"ServerAliveInterval 60\" -o \"ServerAliveCountMax 3\" -L %s:localhost:%s sshreflector@%s -p 9222 -i %s"%(port,port,addr,keypath)
            self.cuisine.run(cmd)


        print ("\n\n\n")
        print ("Reflector:%s"%addr)
        print (out)

    @actionrun(action=True)
    def sshreflector_client(self,remoteids):
        """
        chose a port for remote server which we will reflect to
        @param remoteids :  ovh4,ovh5:2222

        to test
        js 'c=j.tools.cuisine.get("192.168.0.149");c.installer.sshreflector_client("ovh4,ovh5:2222")'

        """

        if remoteids.find(",")!=-1:
            self.cuisine.systemd_remove("autossh") #make sure leftovers are gone
            self.cuisine.run("killall autossh",die=False,showout=False)

            for item in remoteids.split(","):
                self.sshreflector_client(item.strip())
        else:

            self.cuisine.hostfile_set_fromlocal()

            remotecuisine=j.tools.cuisine.get(remoteids)

            package="autossh"
            self.cuisine.package.install(package)


            lpath=os.environ["HOME"]+"/.ssh/reflector"

            if j.do.exists(lpath):
                print("UPLOAD EXISTING SSH KEYS")
            else:
                print("DOWNLOAD SSH KEYS")
                #get private key from reflector
                ftp=remotecuisine.executor.sshclient.getSFTP()
                path="/home/sshreflector/.ssh/reflector"
                ftp.get(path,lpath)
                ftp.close()

            #upload to reflector client
            ftp=self.cuisine.executor.sshclient.getSFTP()
            rpath="/root/.ssh/reflector"
            ftp.put(lpath,rpath)
            self.cuisine.run("chmod 0600 /root/.ssh/reflector")

            if(remotecuisine.executor.addr.find(".")!=-1):
                #is real ipaddress, will put in hostfile as reflector
                addr=remotecuisine.executor.addr
            else:
                a=socket.gethostbyaddr(remotecuisine.executor.addr)
                addr=a[2][0]

            port=remotecuisine.executor.port

            #test if we can reach the port
            if j.sal.nettools.tcpPortConnectionTest(addr,port)==False:
                raise RuntimeError("Cannot not connect to %s:%s"%(addr,port))


            rname="refl_%s"%remotecuisine.executor.addr.replace(".","_")
            rname_short=remotecuisine.executor.addr.replace(".","_")

            self.cuisine.hostfile_set(rname,addr)

            if remotecuisine.file_exists("/home/sshreflector/reflectorclients")==False:
                print ("reflectorclientsfile does not exist")
                remotecuisine.file_write("/home/sshreflector/reflectorclients","%s:%s\n"%(self.cuisine.platformtype.hostname,9800))
                newport=9800
                out2=remotecuisine.file_read("/home/sshreflector/reflectorclients")
            else:
                remotecuisine.file_read("/home/sshreflector/reflectorclients")
                out=remotecuisine.file_read("/home/sshreflector/reflectorclients")
                out2=""
                newport=0
                highestport=0
                for line in out.split("\n"):
                    if line.strip()=="":
                        continue
                    if line.find(self.cuisine.platformtype.hostname)!=-1:
                        newport=int(line.split(":")[1])
                        continue
                    foundport=int(line.split(":")[1])
                    if foundport>highestport:
                        highestport=foundport
                    out2+="%s\n"%line
                if newport==0:
                    newport=highestport+1
                out2+="%s:%s\n"%(self.cuisine.platformtype.hostname,newport)
                remotecuisine.file_write("/home/sshreflector/reflectorclients",out2)

            self.cuisine.file_write("/etc/reflectorclients",out2)

            print("check ssh connection to reflector")
            self.cuisine.run("ssh -i /root/.ssh/reflector -o StrictHostKeyChecking=no sshreflector@%s -p 9222 'ls /'"%rname)
            print ("OK")

            cpath=self.cuisine.run("which autossh")
            cmd="%s -M 0 -N -o ExitOnForwardFailure=yes -o \"ServerAliveInterval 60\" -o \"ServerAliveCountMax 3\" -R %s:localhost:22 sshreflector@%s -p 9222 -i /root/.ssh/reflector"%(cpath,newport,rname)
            self.cuisine.systemd_ensure("autossh_%s"%rname_short, cmd, descr='')

            print ("On %s:%s remote SSH port:%s"%(remotecuisine.executor.addr,port,newport))

    @actionrun(action=True)
    def pi_accesspoint(self,passphrase,name="",dns="8.8.8.8",interface="wlan0"):

        # cmd1='dnsmasq -d'
        if name!="":
            hostname=name
        else:
            hostname=self.cuisine.run("hostname")
        #--dhcp-dns 192.168.0.149
        cpath=self.cuisine.run("which create_ap")
        cmd2='%s %s eth0 gig_%s %s -d'%(cpath,interface,hostname,passphrase)

        giturl="https://github.com/oblique/create_ap"
        self.cuisine.pullGitRepo(url=giturl,dest=None,login=None,passwd=None,depth=1,\
            ignorelocalchanges=True,reset=True,branch=None,revision=None, ssh=False)

        self.cuisine.run("cp /opt/code/create_ap/create_ap /usr/local/bin/")

        START1="""
        [Unit]
        Description=Create AP Service
        Wants=network-online.target
        After=network-online.target

        [Service]
        Type=simple
        ExecStart=$cmd
        KillSignal=SIGINT
        Restart=always
        RestartSec=5

        [Install]
        WantedBy=multi-user.target
        """

        self.cuisine.systemd_ensure("ap",cmd2,descr="accesspoint for local admin",systemdunit=START1)

    @actionrun(action=True)
    def jumpscale(self, rw=False,reset=False):
        """
        install jumpscale, will be done as sandbox
        otherwise will try to install jumpscale inside OS

        @input rw, if True will put overlay filesystem on top of /opt -> /optrw which will allow you to manipulate/debug the install
        @input synclocalcode, sync the local github code to the node (jumpscale) (only when in rw mode)
        @input reset, remove old code (only used when rw mode)
        @input monitor detect local changes & sync (only used when rw mode)
        """

        if reset:
            j.actions.reset("installer")

        def cleanNode(cuisineid):
            """
            make node clean e.g. remove redis, install tmux, stop js8, unmount js8
            """
            cuisine=j.tools.cuisine.get(cuisineid)
            C = """
            set +ex
            pkill redis-server #will now kill too many redis'es, should only kill the one not in docker
            pkill redis #will now kill too many redis'es, should only kill the one not in docker
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
            cuisine.run_script(C)

        def downloadjs8bin(cuisineid):
            """
            install jumpscale8 sandbox in read or readwrite mode
            """
            cuisine=j.tools.cuisine.get(cuisineid)
            C = """
            set -ex
            cd /usr/bin
            rm -f js8
            wget https://stor.jumpscale.org/storx/static/js8
            chmod +x js8
            cd /
            mkdir -p /opt
            """
            cuisine.run_script(C)

        def installJS8SB(cuisineid,rw=False):
            """
            install jumpscale8 sandbox in read or readwrite mode
            """
            cuisine=j.tools.cuisine.get(cuisineid)
            C = """
            set -ex
            cd /usr/bin
            """
            if rw:
                C += "js8 -rw init"
            else:
                C += "js8 init"
            cuisine.run_script(C)

        cleanNode(self.cuisine.id)
        downloadjs8bin(self.cuisine.id)
        installJS8SB(self.cuisine.id)
        # j.actions.add(cleanNode, actionRecover=None, args={"cuisineid":self.cuisine.id}, die=True, stdOutput=True, errorOutput=True, retry=1,deps=None)
        # j.actions.add(downloadjs8bin, actionRecover=None, args={"cuisineid":self.cuisine.id}, die=True, stdOutput=True, errorOutput=True, retry=3,deps=None)
        # j.actions.add(installJS8SB, actionRecover=None, args={"cuisineid":self.cuisine.id,'rw':rw}, die=True, stdOutput=True, errorOutput=True, retry=1,deps=None)
        # j.actions.run()


    @actionrun(action=True)
    def pip(self):
        self.base()
        self.pythonDevelop()
        cmd="""
            cd /tmp
            rm -rf get-pip.py
            wget https://bootstrap.pypa.io/get-pip.py
        """
        self.cuisine.run_script(cmd)
        self.cuisine.run("cd /tmp;python3.5 get-pip.py")

    @actionrun(action=True)
    def pythonDevelop(self):
        C="""
        libpython3.5-dev
        python3.5-dev
        libffi-dev
        gcc
        build-essential
        autoconf
        libtool
        pkg-config
        libpq-dev
        libsqlite3-dev
        #net-tools
        """
        self.cuisine.package.multiInstall(C)

    @actionrun(action=True)
    def base(self):
        C="""
        sudo
        wget
        curl
        git
        openssl
        mc
        net-tools
        """
        self.cuisine.package.multiInstall(C)

    #@todo (*1*) installer for golang
    #@todo (*1*) installer for caddy
    #@todo (*1*) installer for etcd
    #@todo (*1*) installer for skydns
    #@todo (*1*) installer for aydostor


    @actionrun(action=True)
    def webProxyServer(self):

        self.cuisine.package.install("polipo")

        forbiddentunnels="""
        # simple case, exact match of hostnames
        www.massfuel.com

        # match hostname against regexp
        \.hitbox\.

        # match hostname and port against regexp
        # this will block tunnels to example.com but also  www.example.com
        # for ports in the range 600-999
        # Also watch for effects of 'tunnelAllowedPorts'
        example.com\:[6-9][0-9][0-9]

        # random examples
        \.liveperson\.
        \.atdmt\.com
        .*doubleclick\.net
        .*webtrekk\.de
        ^count\..*
        .*\.offerstrategy\.com
        .*\.ivwbox\.de
        .*adwords.*
        .*\.sitestat\.com
        \.xiti\.com
        webtrekk\..*
        """
        self.cuisine.file_write("/etc/polipo/forbiddenTunnels",forbiddentunnels)

        # dnsNameServer

        CONFIG="""
            ### Basic configuration
            ### *******************

            # Uncomment one of these if you want to allow remote clients to
            # connect:

            # proxyAddress = "::0"        # both IPv4 and IPv6
            proxyAddress = "0.0.0.0"    # IPv4 only

            # If you do that, you'll want to restrict the set of hosts allowed to
            # connect:

            # allowedClients = 127.0.0.1, 134.157.168.57
            # allowedClients = 127.0.0.1, 134.157.168.0/24

            # Uncomment this if you want your Polipo to identify itself by
            # something else than the host name:

            # proxyName = "polipo.example.org"

            # Uncomment this if there's only one user using this instance of Polipo:

            # cacheIsShared = false

            # Uncomment this if you want to use a parent proxy:

            # parentProxy = "squid.example.org:3128"

            # Uncomment this if you want to use a parent SOCKS proxy:

            # socksParentProxy = "localhost:9050"
            # socksProxyType = socks5

            # Uncomment this if you want to scrub private information from the log:

            # scrubLogs = true


            ### Memory
            ### ******

            # Uncomment this if you want Polipo to use a ridiculously small amount
            # of memory (a hundred C-64 worth or so):

            # chunkHighMark = 819200
            # objectHighMark = 128

            # Uncomment this if you've got plenty of memory:

            chunkHighMark = 100331648
            objectHighMark = 16384


            ### On-disk data
            ### ************

            # Uncomment this if you want to disable the on-disk cache:

            # diskCacheRoot = ""

            # Uncomment this if you want to put the on-disk cache in a
            # non-standard location:

            # diskCacheRoot = "~/.polipo-cache/"

            # Uncomment this if you want to disable the local web server:

            # localDocumentRoot = ""

            # Uncomment this if you want to enable the pages under /polipo/index?
            # and /polipo/servers?.  This is a serious privacy leak if your proxy
            # is shared.

            # disableIndexing = false
            # disableServersList = false


            ### Domain Name System
            ### ******************

            # Uncomment this if you want to contact IPv4 hosts only (and make DNS
            # queries somewhat faster):

            # dnsQueryIPv6 = no

            # Uncomment this if you want Polipo to prefer IPv4 to IPv6 for
            # double-stack hosts:

            # dnsQueryIPv6 = reluctantly

            # Uncomment this to disable Polipo's DNS resolver and use the system's
            # default resolver instead.  If you do that, Polipo will freeze during
            # every DNS query:

            # dnsUseGethostbyname = yes


            ### HTTP
            ### ****

            # Uncomment this if you want to enable detection of proxy loops.
            # This will cause your hostname (or whatever you put into proxyName
            # above) to be included in every request:

            # disableVia=false

            # Uncomment this if you want to slightly reduce the amount of
            # information that you leak about yourself:

            # censoredHeaders = from, accept-language
            censorReferer = maybe

            # Uncomment this if you're paranoid.  This will break a lot of sites,
            # though:

            # censoredHeaders = set-cookie, cookie, cookie2, from, accept-language
            # censorReferer = true

            # Uncomment this if you want to use Poor Man's Multiplexing; increase
            # the sizes if you're on a fast line.  They should each amount to a few
            # seconds' worth of transfer; if pmmSize is small, you'll want
            # pmmFirstSize to be larger.

            # Note that PMM is somewhat unreliable.

            # pmmFirstSize = 16384
            # pmmSize = 8192

            # Uncomment this if your user-agent does something reasonable with
            # Warning headers (most don't):

            relaxTransparency = maybe

            # Uncomment this if you never want to revalidate instances for which
            # data is available (this is not a good idea):

            # relaxTransparency = yes

            # Uncomment this if you have no network:

            # proxyOffline = yes

            # Uncomment this if you want to avoid revalidating instances with a
            # Vary header (this is not a good idea):

            # mindlesslyCacheVary = true

            # Uncomment this if you want to add a no-transform directive to all
            # outgoing requests.

            # alwaysAddNoTransform = true

            disableIndexing = false

            """
        self.cuisine.file_write("/etc/polipo/config",CONFIG)

        print ("INSTALL OK")
        print ("to see status: point webbrowser to")
        print ("http://%s:8123/polipo/status?"%self.cuisine.executor.addr)
        # print ("http://%s:8123/polipo/status?"%self.cuisine.executor.addr)
        print ("configure your webproxy client to use %s on tcp port 8123"%self.cuisine.executor.addr)

        self.cuisine.run("killall polipo",die=False)

        cmd=self.cuisine.run("which polipo")

        self.cuisine.systemd.ensure("polipo",cmd)

        self.cuisine.avahi.install()

        # if self.cuisine.isUbuntu():
        #     self.cuisine.run("ufw allow 8123")

    @actionrun(action=True)
    def installArchLinuxToSDCard(self,redownload=False):
        """
        will only work if 1 sd card found of 8 or 16 GB, be careful will overwrite the card
        executor = a linux machine

        executor=j.tools.executor.getSSHBased(addr="192.168.0.23", port=22,login="root",passwd="rooter",pushkey="ovh_install")
        j.tools.develop.installer.installArchLinuxToSDCard(executor)

        """

        j.actions.setRunId("installArchSD")

        def partition(cuisineid,deviceid,size):
            cuisine=j.tools.cuisine.get(cuisineid)

            cmd="parted -s /dev/%s mklabel msdos mkpar primary fat32 2 100M mkpart primary ext4 100M 100"%deviceid
            cmd+="%"
            self.cuisine.run(cmd)
            self.cuisine.run("umount /mnt/boot",die=False)
            self.cuisine.run("umount /mnt/root",die=False)
            self.cuisine.run("mkfs.vfat /dev/%s1"%deviceid)
            self.cuisine.run("mkdir -p /mnt/boot;mount /dev/%s1 /mnt/boot"%deviceid)
            self.cuisine.run("mkfs.ext4 /dev/%s2"%deviceid)
            self.cuisine.run("mkdir -p /mnt/root;mount /dev/%s2 /mnt/root"%deviceid)
            if redownload:
                self.cuisine.file_unlink("/mnt/ArchLinuxARM-rpi-2-latest.tar.gz")
            if not self.cuisine.file_exists("/mnt/ArchLinuxARM-rpi-2-latest.tar.gz"):
                self.cuisine.run("cd /mnt;wget http://archlinuxarm.org/os/ArchLinuxARM-rpi-2-latest.tar.gz")
            self.cuisine.run("cd /mnt;bsdtar -xpf ArchLinuxARM-rpi-2-latest.tar.gz -C root")
            self.cuisine.run("sync")
            self.cuisine.run("cd /mnt;mv root/boot/* boot")

            self.cuisine.run("echo 'PermitRootLogin=yes'>>'/mnt/root/etc/ssh/sshd_config'")


            self.cuisine.run("umount /mnt/boot",die=False)
            self.cuisine.run("umount /mnt/root",die=False)


        def findDevices():
            devs=[]
            for line in self.cuisine.run("lsblk -b -o TYPE,NAME,SIZE").split("\n"):
                if line.startswith("disk"):
                    while line.find("  ")>0:
                        line=line.replace("  "," ")
                    ttype,dev,size=line.split(" ")
                    size=int(size)
                    if size>30000000000 and size < 32000000000:
                        devs.append((dev,size))
                    if size>15000000000 and size < 17000000000:
                        devs.append((dev,size))
                    if size>7500000000 and size < 8500000000:
                        devs.append((dev,size))
            if len(devs)==0:
                raise RuntimeError("could not find flash disk device, (need to find at least 1 of 8,16 or 32 GB size)"%devs)
            return devs


        devs=findDevices()

        for deviceid,size in devs:
            j.actions.add(partition, actionRecover=None, args={"cuisineid":self.cuisine.id,'deviceid':deviceid,"size":size}, die=True, stdOutput=True, errorOutput=True, retry=1,deps=None)

        j.actions.run()


    def mongodb(self, start=True):
        j.actions.setRunId("installMongo")
        rc, out = self.cuisine.run('which mongod', die=False)
        if rc== 0:
            print('mongodb is already installed')
            return

        appbase = '/usr/local/bin/'

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
            self.cuisine.file_download(url, to=j.dirs.tmpDir,overwrite=False,expand=True)
            tarpath = self.cuisine.fs_find(j.dirs.tmpDir,recursive=True,pattern="*mongodb*.tgz",type='f')[0]
            self.cuisine.file_expand(tarpath,j.dirs.tmpDir)
            extracted = self.cuisine.fs_find(j.dirs.tmpDir,recursive=True,pattern="*mongodb*",type='d')[0]
            for file in self.cuisine.fs_find('%s/bin/' %extracted,type='f'):
                self.cuisine.file_copy(file,appbase)

        self.cuisine.dir_ensure('/optvar/data/db')

        if start:
            self.cuisine.tmux.executeInScreen("main", screenname="mongodb", cmd="mongod --dbpath /optvar/data/db", user='root')


    def __str__(self):
        return "cuisine.installer:%s:%s"%(self.executor.addr,self.executor.port)

    __repr__=__str__
