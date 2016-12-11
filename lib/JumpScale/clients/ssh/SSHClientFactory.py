from JumpScale import j

import paramiko
from paramiko.ssh_exception import SSHException, BadHostKeyException, AuthenticationException
import time
import socket

import threading
import queue

from SSHClient import SSHClient


class SSHClientFactory():

    def __init__(self):
        self.__jslocation__ = "j.clients.ssh"
        self.logger = j.logger.get("j.clients.ssh")
        self.cache = {}
        self.loadSSHKeys = j.do.loadSSHKeys
        self._addSSHAgentToBashProfile = j.do._addSSHAgentToBashProfile
        self._initSSH_ENV = j.do._initSSH_ENV
        self._getSSHSocketpath = j.do._getSSHSocketpath
        self.loadSSHKeys = j.do.loadSSHKeys
        self.getSSHKeyPathFromAgent = j.do.getSSHKeyPathFromAgent
        self.getSSHKeyFromAgentPub = j.do.getSSHKeyFromAgentPub
        self.listSSHKeyFromAgent = j.do.listSSHKeyFromAgent
        self.ensure_keyname = j.do.ensure_keyname
        self.authorize_user = j.do.authorize_user
        self.authorize_root = j.do.authorize_root
        self.authorizeSSHKey = j.do.authorizeSSHKey
        self._loadSSHAgent = j.do._loadSSHAgent
        self.checkSSHAgentAvailable = j.do.checkSSHAgentAvailable

    def reset(self):
        for key, client in self.cache.items():
            client.close()
        self.cache = {}

    def get(self, addr='', port=22, login="root", passwd=None, stdout=True, forward_agent=True, allow_agent=True,
            look_for_keys=True, timeout=5, key_filename=None, passphrase=None, die=True, usecache=True):
        """
        gets an ssh client.
        @param addr: the server to connect to
        @param port: port to connect to
        @param login: the username to authenticate as
        @param passwd: leave empty if logging in with sshkey
        @param stdout: show output
        @param foward_agent: fowrward all keys to new connection
        @param allow_agent: set to False to disable connecting to the SSH agent
        @param look_for_keys: set to False to disable searching for discoverable private key files in ~/.ssh/
        @param timeout: an optional timeout (in seconds) for the TCP connect
        @param key_filename: the filename to try for authentication
        @param passphrase: a password to use for unlocking a private key
        @param die: die on error
        @param usecache: use cached client. False to get a new connection

        If password is passed, sshclient will try to authenticated with login/passwd.
        If key_filename is passed, it will override look_for_keys and allow_agent and try to connect with this key.
        """

        key = "%s_%s_%s_%s" % (
            addr, port, login, j.data.hash.md5_string(str(passwd)))

        if key in self.cache and usecache:
            try:
                if not self.cache[key].transport.is_active():
                    usecache = False
            except Exception:
                usecache = False
        if key not in self.cache or usecache is False:
            self.cache[key] = SSHClient(addr, port, login, passwd, stdout=stdout, forward_agent=forward_agent, allow_agent=allow_agent,
                                        look_for_keys=look_for_keys, key_filename=key_filename, passphrase=passphrase, timeout=timeout)

        return self.cache[key]

    def removeFromCache(self, client):
        key = "%s_%s_%s_%s" % (
            client.addr, client.port, client.login, j.data.hash.md5_string(str(client.passwd)))
        if key in self.cache:
            self.cache.pop(key)

    def getSSHKeyFromAgentPub(self, keyname="", die=True):
        rc, out, err = j.tools.cuisine.local.core.run("ssh-add -L", die=False)
        if rc > 1:
            err = "Error looking for key in ssh-agent: %s", out
            if die:
                raise j.exceptions.RuntimeError(err)
            else:
                self.logger.error(err)
                return None

        if keyname == "":
            paths = []
            for line in out.splitlines():
                line = line.strip()
                paths.append(line.split(" ")[-1])
            if len(paths) == 0:
                raise j.exceptions.RuntimeError(
                    "could not find loaded ssh-keys")

            path = j.tools.console.askChoice(
                paths, "Select ssh key to push (public part only).")
            keyname = j.sal.fs.getBaseName(path)

        for line in out.splitlines():
            delim = (".ssh/%s" % keyname)
            if line.endswith(delim):
                content = line.strip()
                content = content
                return content
        err = "Did not find key with name:%s, check its loaded in ssh-agent with ssh-add -l" % keyname
        if die:
            raise j.exceptions.RuntimeError(err)
        else:
            self.logger.error(err)
        return None

    def close(self):
        for key, client in self.cache.items():
            client.close()
