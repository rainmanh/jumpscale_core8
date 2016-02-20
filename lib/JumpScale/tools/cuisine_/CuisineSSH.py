
from JumpScale import j
import netaddr
import os

class CuisineSSH():

    def __init__(self,executor,cuisine):
        self.executor=executor
        self.cuisine=cuisine

    def test_login(self,passwd,port=22,range=None,onlyplatform="arch"):
        login="root"
        res=[]
        for item in self.scan(range=range):
            print ("test for login/passwd on %s"%item)
            client=j.clients.ssh.get(item,port,login,passwd)
            try:
                testoutput=client.connectTest(timeout=1,die=False)
            except Exception as e:
                print ("  NOT OK")
                continue
            if testoutput==False:
                print ("  NOT OK")
                continue
            executor=j.tools.executor.getSSHBased(item,port,login,passwd,checkok=True)
            if onlyplatform!="":
                if not str(executor.cuisine.platformtype).startswith(onlyplatform):
                    continue
            print("  RESPONDED!!!")
            res.append(item)
        return res

    def test_login_pushkey(self,passwd,keyname,port=22,range=None,changepasswdto="",onlyplatform="arch"):
        """
        """
        login="root"
        done=[]
        for item in self.test_login(passwd,port,range,onlyplatform=onlyplatform):
            keypath=j.do.joinPaths(os.environ["HOME"],".ssh",keyname+".pub")
            if j.do.exists(keypath):
                key=j.do.readFile(keypath)
                executor=j.tools.executor.getSSHBased(item,port,login,passwd,checkok=True)
                executor.cuisine.ssh.authorize(user="root",key=key)
                if changepasswdto!="":
                    executor.cuisine.user.passwd(login, changepasswdto, encrypted_passwd=False)
            else:
                raise RuntimeError("Cannot find key:%s"%keypath)
            done.append(item)
        return done

    def scan(self,range=None,ips={},port=22):
        """
        @param range in format 192.168.0.0/24
        if range not specified then will take all ranges of local ip addresses (nics)
        """
        if range==None:
            res=self.cuisine.net.get_info()
            for item in res:
                cidr=item['cidr']

                name=item['name']
                if not name.startswith("docker") and name not in ["lo"]:
                    if len(item['ip'])>0:
                        ip=item['ip'][0]
                        ipn=netaddr.IPNetwork(ip+"/"+str(cidr))
                        range=str(ipn.network)+"/%s"%cidr
                        ips=self.scan(range,ips)
            return ips
        else:
            try:
                # out=self.cuisine.run("nmap -p 22 %s | grep for"%range,showout=False)
                out=self.cuisine.run("nmap %s -p %s --open -oX $tmpDir/nmap"%(range,port),showout=False,force=False,action=True)
            except Exception as e:
                if str(e).find("command not found")!=-1:
                    self.cuisine.package.install("nmap")
                    # out=self.cuisine.run("nmap -p 22 %s | grep for"%range)
                    out=self.cuisine.run("nmap %s -p %s --open -oX $tmpDir/nmap"%(range,port),showout=False,force=False,action=True)
            out=self.cuisine.file_read("$tmpDir/nmap")
            import xml.etree.ElementTree as ET
            root = ET.fromstring(out)
            for child in root:
                if child.tag=="host":
                    ip=None
                    mac=None
                    for addr in child.findall("address"):
                        if addr.get("addrtype")=="ipv4":
                            ip=addr.get("addr")

                    for addr in child.findall("address"):
                        if addr.get("addrtype")=="mac":
                            mac=addr.get("addr")

                    if ip!=None:
                        ips[ip]={"mac":mac}

            # for line in out.split("\n"):
            #     ip=line.split("for")[1].strip()
            #     if ip.find("(")!=-1:
            #         ip=ip.split("(")[1].strip(")").strip()
            #     if ip not in ips:

            #         ips.append(ip)
            return ips


    def keygen(self,user, keytype="dsa"):
        """Generates a pair of ssh keys in the user's home .ssh directory."""
        user=user.strip()
        d = self.user.check(user)
        assert d, "User does not exist: %s" % (user)
        home = d["home"]
        key_file = home + "/.ssh/id_%s.pub" % keytype
        if not self.cuisine.file_exists(key_file):
            self.cuisine.dir_ensure(home + "/.ssh", mode="0700", owner=user, group=user)
            self.cuisine.run("ssh-keygen -q -t %s -f '%s/.ssh/id_%s' -N ''" %
                (keytype, home, keytype))
            self.cuisine.file_attribs(home + "/.ssh/id_%s" % keytype, owner=user, group=user)
            self.cuisine.file_attribs(home + "/.ssh/id_%s.pub" % keytype, owner=user, group=user)
            return key_file
        else:
            return key_file

    def authorize(self,user, key):
        """Adds the given key to the '.ssh/authorized_keys' for the given
        user."""
        sudomode = self.cuisine.sudomode
        self.cuisine.set_sudomode()

        user=user.strip()
        d = self.cuisine.user.check(user, need_passwd=False)
        if d==None:
            raise RuntimeError("did not find user:%s"%user)
        group = d["gid"]
        keyf  = d["home"] + "/.ssh/authorized_keys"
        if key[-1] != "\n":
            key += "\n"
        ret = None

        if self.cuisine.file_exists(keyf):
            d = self.cuisine.file_read(keyf)
            if self.cuisine.file_read(keyf).find(key[:-1]) == -1:
                self.cuisine.file_append(keyf, key)
                ret = False
            else:
                ret = True
        else:
            # Make sure that .ssh directory exists, see #42
            self.cuisine.dir_ensure(os.path.dirname(keyf), owner=user, group=group, mode="700")
            self.cuisine.file_write(keyf, key,             owner=user, group=group, mode="600")
            ret = False

        self.cuisine.sudomode = sudomode
        return ret

    def unauthorize(self,user, key):
        """Removes the given key to the remote '.ssh/authorized_keys' for the given
        user."""
        key   = key.strip()
        d     = user.check(user, need_passwd=False)
        group = d["gid"]
        keyf  = d["home"] + "/.ssh/authorized_keys"
        if self.cuisine.file_exists(keyf):
            self.cuisine.file_write(keyf, "\n".join(_ for _ in file_read(keyf).split("\n") if _.strip() != key), owner=user, group=group, mode="600")
            return True
        else:
            return False

    def sshagent_add(self,path,removeFirst=True):
        """
        @path is path to private key
        """
        print ("add ssh key to ssh-agent: %s"%path)
        self.cuisine.run("ssh-add -d '%s'"%path,die=False,showout=False)
        keys=self.cuisine.run("ssh-add -l",showout=False)
        if path in keys:
            raise RuntimeError("ssh-key is still loaded in ssh-agent, please remove manually")
        self.cuisine.run("ssh-add '%s'"%path,showout=False)

    def sshagent_remove(self,path):
        """
        @path is path to private key
        """
        print ("remove ssh key to ssh-agent: %s"%path)
        self.cuisine.run("ssh-add -d '%s'"%path,die=False,showout=False)
        keys=self.cuisine.run("ssh-add -l",showout=False)
        if path in keys:
            raise RuntimeError("ssh-key is still loaded in ssh-agent, please remove manually")
