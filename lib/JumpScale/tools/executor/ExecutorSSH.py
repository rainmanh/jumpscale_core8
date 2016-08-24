from JumpScale import j
from ExecutorBase import *
import os


class ExecutorSSH(ExecutorBase):

    def __init__(self, addr, port, dest_prefixes={}, login="root",
                 passwd=None, debug=False, allow_agent=True,
                 look_for_keys=True, checkok=True, timeout=5):
        # DO NOT USE THIS TO PUSH A KEY!!!
        ExecutorBase.__init__(self, dest_prefixes=dest_prefixes, debug=debug, checkok=checkok)
        self.logger = j.logger.get("j.tools.executor.ssh")
        self.id = '%s:%s' % (addr, port)  # do not put login name in key,
        self.addr = addr
        self._port = int(port)
        self._login = login
        self._passwd = passwd
        if passwd != None:
            look_for_keys = False
            allow_agent = False
        self.allow_agent = allow_agent
        self.look_for_keys = look_for_keys
        self._sshclient = None
        self.type = "ssh"
        self.timeout = timeout

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
        if passwd != None:
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
            return self._getSSHClient()
        return self._sshclient

    def _getSSHClient(self, key_filename=None, passphrase=None):
        self._sshclient = j.clients.ssh.get(self.addr, self.port, login=self.login, passwd=self.passwd,
                                            allow_agent=self.allow_agent, look_for_keys=self.look_for_keys,
                                            key_filename=key_filename, passphrase=passphrase,
                                            timeout=self.timeout, usecache=False)  # TODO: add passphrase fo sshkeys (not urgent)

        return self._sshclient

    def authorizeKey(self, pubkey=None, keyname=None, passphrase=None, login="root"):
        """
        This will authenticate the ssh client to access the target machine
        using the given pubkey, If pushkey is set, that key will be loaded,
        and used instead.

        :param pubkey: Public key to authenticate with (is the content)
        :param pushkey: name to public key, will get from ssh-agent
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

    def execute(self, cmds, die=True, checkok=None, async=False, showout=True, timeout=0, env={}):
        """
        @param naked means will not manipulate cmd's to show output in different way
        @param async is not used method, but is only used for interface comaptibility
        return (rc,out,err)
        """
        if env:
            self.env.update(env)
        if showout:
            self.logger.debug("cmd: %s" % cmds)
        cmds2 = self._transformCmds(cmds, die, checkok=checkok)

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
            self.docheckok(cmds, out)

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
