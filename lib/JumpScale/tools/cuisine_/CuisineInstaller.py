
from JumpScale import j
import os


class CuisineInstaller(object):

    def __init__( self,cuisine ):
        self.cuisine=cuisine


    def redis(self):
        defport=6379
        if self.cuisine.process_tcpport_check(defport,"redis"):
            print ("no need to install, already there & running")
            return 

        if self.cuisine.isUbuntu:
            package="redis-server"
        else:
            package="redis"
        
        self.cuisine.package_install(package)
        self.cuisine.package_start(package)

        if self.cuisine.process_tcpport_check(defport,"redis")==False:
            raise RuntimeError("Could not install redis, port was not running")

    def sshreflector(self,reset=False):

        port=9222

        package="dropbear"
        self.cuisine.package_install(package)

        passwd=j.data.idgenerator.generateGUID()
        self.cuisine.user_ensure("sshreflector", passwd=passwd, home="/home/sshreflector", uid=None, gid=None, shell=None, fullname=None, encrypted_passwd=True, group=None)

        self.cuisine.run('ufw allow %s'%port,die=False)

        self.cuisine.dir_ensure("/home/sshreflector/.ssh", recursive=True, mode=None, owner="sshreflector", group="sshreflector")

        cmd="dropbear -R -F -E -p 9222 -w"

        path="/home/sshreflector/.ssh/reflector"
        if reset:
            self.cuisine.file_unlink(path)
        if not self.cuisine.file_exists(path):
            self.cuisine.run("ssh-keygen -f %s -N ''"%path)

        ftp=self.cuisine.executor.sshclient.getSFTP()
        lpath=os.environ["HOME"]+"/.ssh/reflector"
        ftp.get(path,lpath)
        ftp.get(path+".pub",lpath+".pub")

        j.do.chmod(lpath,0o600)
        j.do.chmod(lpath+".pub",0o600)

        #authorize remote server to accept now copied private key
        self.cuisine.ssh_authorize("sshreflector",j.do.readFile(lpath+".pub"))

        self.cuisine.run("chmod 0644 /home/sshreflector/.ssh/*")
        self.cuisine.run("chown -R sshreflector:sshreflector /home/sshreflector/.ssh/")

        cpath=self.cuisine.run("which dropbear")

        cmd="%s -R -F -E -p 9222 -w -s -g -j"%cpath
        self.cuisine.systemd_ensure("reflector", cmd, descr='')

        # self.cuisine.package_start(package)

        if self.cuisine.process_tcpport_check(port,"dropbear")==False:
            raise RuntimeError("Could not install redis, port was not running")


    def sshreflector_client(self,remotecuisine):
        """
        chose a port for remote server which we will reflect to

        to test
        js 'remote=j.tools.cuisine.get("ovh4:9022");c=j.tools.cuisine.get("192.168.0.149");c.installer.sshreflector_client(remote)'

        """

        package="autossh"
        self.cuisine.package_install(package)

        #get private key from reflector
        path="/home/sshreflector/.ssh/reflector"
        lpath=j.dirs.tmpDir+"/reflector"
        ftp=remotecuisine.executor.sshclient.getSFTP()
        ftp.get(path,lpath)
        ftp.close()
        ftp=self.cuisine.executor.sshclient.getSFTP()
        rpath="/root/.ssh/reflector"
        ftp.put(lpath,rpath)
        self.cuisine.run("chmod 0600 /root/.ssh/reflector")


        if(remotecuisine.executor.addr.find(".")==-1):
            #is real ipaddress, will put in hostfile as reflector
            addr=remotecuisine.executor.addr
        else:
            a=socket.gethostbyaddr(remotecuisine.executor.addr)
            addr=a[2][0]

        port=remotecuisine.executor.port

        #test if we can reach the port
        if j.sal.nettools.tcpPortConnectionTest(addr,port)==False:
            raise RuntimeError("Cannot not connect to %s:%s"%(addr,port))

        self.cuisine.hostfile_set("reflector",addr)

        if remotecuisine.file_exists("/home/sshreflector/reflectorclients")==False:
            remotecuisine.file_write("/home/sshreflector/reflectorclients","%s:%s\n"%(self.cuisine.platformtype.hostname,9800))
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

        cpath=self.cuisine.run("which autossh")
        cmd="%s -M 20000 -N -R %s:localhost:22 sshreflector@reflector -p 9222 -i /root/.ssh/reflector"%(cpath,newport)
        self.cuisine.systemd_ensure("autossh", cmd, descr='')

        print ("On %s:%s remote SSH port:%s"%(remotecuisine.executor.addr,port,newport)
        

