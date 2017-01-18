from JumpScale import j
from ExecutorBase import *
import os


class ExecutorSSH(ExecutorBase):

    def __init__(self, addr='', port=22, login="root",
                 passwd=None,  allow_agent=True, debug=False,
                 look_for_keys=True, checkok=True, timeout=5, key_filename=None, passphrase=None):

        ExecutorBase.__init__(self,  debug=debug, checkok=checkok)

        self.addr = addr
        self.port = port
        self.type = "ssh"

        self._port = int(port)
        self._login = login
        self._passwd = passwd
        if passwd is not None:
            look_for_keys = False
            allow_agent = False
        self.allow_agent = allow_agent
        self.look_for_keys = look_for_keys
        self._sshclient = None
        self.timeout = timeout
        self.proxycommand = None
        self.key_filename = key_filename
        self.passphrase = passphrase
        self._id = None

    @property
    def logger(self):
        if self._logger is None:
            self._logger = j.logger.get("executor.%s" % self.addr)
        return self._logger

    def getMacAddr(self):
        print("Get maccaddr")
        rc, out, err = self.execute("ifconfig | grep HWaddr", showout=False)
        res = {}
        for line in out.split("\n"):
            line = line.strip()
            excl = ["dummy", "docker", "lxc", "mie", "veth", "vir", "vnet", "zt", "vms", "weave", "ovs"]
            if line == "":
                continue
            check = True
            for item in excl:
                if line.startswith(item):
                    check = False
            addr = line.split("HWaddr")[-1].strip()
            name = line.split(" ")[0]

            if check:
                res[name] = addr

        if "eth0" in res:
            self.macaddr = res["eth0"]
        else:
            keys = [item for item in res.keys()]
            keys.sort()
            self.macaddr = res[keys[0]]

        return self.macaddr

    @property
    def id(self):
        if self._id is None:
            self._id = '%s_%s' % (self.addr, self.getMacAddr())
        return self._id

        # TODO: *1 could be this does not work in docker, lets check

    @property
    def login(self):
        return self._login

    @login.setter
    def login(self, val):
        self._login = val
        self._sshclient = None

    @property
    def passwd(self):
        return self._passwd

    @passwd.setter
    def passwd(self, passwd):
        if passwd is not None:
            self.look_for_keys = False
            self.allow_agent = False
        self._passwd = passwd
        self._sshclient = None

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, val):
        self._port = int(val)
        self._sshclient = None

    @property
    def sshclient(self):
        if self._sshclient is None:
            return self._getSSHClient(key_filename=self.key_filename, passphrase=self.passphrase)
        return self._sshclient

    def _getSSHClient(self, key_filename=None, passphrase=None):
        self._sshclient = j.clients.ssh.get(self.addr, self.port, login=self.login, passwd=self.passwd,
                                            allow_agent=self.allow_agent, look_for_keys=self.look_for_keys,
                                            key_filename=key_filename, passphrase=passphrase,
                                            timeout=self.timeout, usecache=False)

        return self._sshclient

    def getSSHViaProxy(self, jumphost, jmpuser, host, username, port, identityfile, proxycommand=None):
        self._sshclient = j.clients.ssh.get()
        self._login = jmpuser
        self.addr = jumphost
        jmpuser = self._login
        jumphost = self.addr
        if proxycommand is None:
            proxycommand = """ssh -A -i {identityfile} -q {jmpuser}@{jumphost} nc -q0 {host} {port}""".format(
                **locals())
        self._sshclient.connectViaProxy(host, username, port, identityfile, proxycommand)
        self.id = 'jump:%s:%s:%i' % (jumphost, host, port)
        return self

    def jumpto(self, addr='', port=22, dest_prefixes={}, login="root",
               passwd=None, debug=False, allow_agent=True,
               look_for_keys=True, checkok=True, timeout=5,
               identityfile=None):
        if identityfile is None:
            raise NotImplementedError("you have to use an identityfile for now")

        def escape(s):
            return s.replace("'", "'\"'\"'")

        jumpedto = j.clients.ssh.get(addr=addr, port=port, login=login,
                                     usecache=False)
        jmpuser = self._login
        jumphost = self.addr
        if self.proxycommand is not None:
            proxy_part = " -o ProxyCommand='{proxy_command}'".format(
                proxy_command=escape(self.proxycommand))
        else:
            proxy_part = ""
        proxy_command = "ssh -A -i {identityfile} {old_login}@{old_ip} \
            -p {old_port} {proxy_part} nc -q0 {ip} {port}".format(
            ip=addr, port=port, old_port=self.port, old_ip=self.addr,
            old_login=self.login, identityfile=identityfile,
            proxy_part=proxy_part)
        ex = ExecutorSSH(addr=addr, port=port, dest_prefixes=dest_prefixes,
                         login=login, passwd=passwd, debug=debug, allow_agent=allow_agent,
                         look_for_keys=look_for_keys, checkok=checkok, timeout=timeout)
        ex.proxycommand = proxy_command

        jumpedto.connectViaProxy(addr, login, port, identityfile, proxy_command)
        ex._sshclient = jumpedto
        return ex

    def authorizeKey(self, pubkey=None, keyname=None, passphrase=None, login="root"):
        """
        This will authenticate the ssh client to access the target machine
        using the given pubkey.

        :param pubkey: Public key to authenticate with (is the content)
        :return:
        """

        if not pubkey:
            path = j.do.getSSHKeyPathFromAgent(keyname, die=True)
            self._getSSHClient(path, passphrase)  # should be the correct client now

        self.sshclient._cuisine = self.cuisine

        # was private key,need to add .pub to have public key
        path = '%s.pub' % path
        if j.sal.fs.exists(path):
            pubkey = j.sal.fs.fileGetContents(path)
        else:
            raise j.exceptions.RuntimeError("Could not find key:%s" % path)
        self._sshclient.ssh_authorize(login, pubkey)

    def executeRaw(self, cmd, die=True, showout=False):
        return self.sshclient.execute(cmd, die=die, showout=showout)

    def execute(self, cmds, die=True, checkok=None, showout=True, timeout=0, env={}):
        """
        @param naked means will not manipulate cmd's to show output in different way
        @param async is not used method, but is only used for interface comaptibility
        return (rc,out,err)
        """
        if env:
            self.env.update(env)
        if showout:
            self.logger.debug("cmd: %s" % cmds)

        if checkok is None:
            checkok = self.checkok

        cmds2 = self._transformCmds(cmds, die, checkok=checkok, env=env)

        if cmds.find("\n") != -1:
            if showout:
                self.logger.info("EXECUTESCRIPT} %s:%s:\n%s" % (self.addr, self.port, cmds))
            # else:
            #     self.logger.debug("EXECUTESCRIPT} %s:%s:\n%s"%(self.addr, self.port, cmds))
            sshkey = self.sshclient.key_filename or ""
            rc, out, err = j.do.executeBashScript(content=cmds2, path=None, die=die,
                                                  remote=self.addr, sshport=self.port, sshkey=sshkey)
        else:
            # online command, we use cuisine
            if showout:
                self.logger.info("EXECUTE %s:%s: %s" % (self.addr, self.port, cmds))
            # else:
            #     self.logger.debug("EXECUTE %s:%s: %s"%(self.addr, self.port, cmds))
            rc, out, err = self.sshclient.execute(cmds2, die=die, showout=showout)

        if checkok and die:
            out = self.docheckok(cmds, out)

        return rc, out, err

    def upload(self, source, dest, dest_prefix="", recursive=True, createdir=True):

        if dest_prefix != "":
            dest = j.sal.fs.joinPaths(dest_prefix, dest)
        if dest[0] != "/":
            raise j.exceptions.RuntimeError("need / in beginning of dest path")
        dest = "root@%s:%s" % (self.addr, dest)
        j.sal.fs.copyDirTree(source, dest, keepsymlinks=True, deletefirst=False,
                             overwriteFiles=True, ignoredir=[".egg-info", ".dist-info"], ignorefiles=[".egg-info"], rsync=True,
                             ssh=True, sshport=self.port, recursive=recursive, createdir=createdir)

    def download(self, source, dest, source_prefix="", recursive=True):
        if source_prefix != "":
            source = j.sal.fs.joinPaths(source_prefix, source)
        if source[0] != "/":
            raise j.exceptions.RuntimeError("need / in beginning of source path")
        source = "root@%s:%s" % (self.addr, source)
        j.sal.fs.copyDirTree(source, dest, keepsymlinks=True, deletefirst=False,
                             overwriteFiles=True, ignoredir=[".egg-info", ".dist-info"], ignorefiles=[".egg-info"], rsync=True,
                             ssh=True, sshport=self.port, recursive=recursive)
