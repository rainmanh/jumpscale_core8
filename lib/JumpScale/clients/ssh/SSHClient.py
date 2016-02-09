from JumpScale import j

import paramiko
from paramiko.ssh_exception import SSHException, BadHostKeyException, AuthenticationException
import time
import io
import socket

class SSHClientFactory(object):

    def __init__(self):
        self.__jslocation__ = "j.clients.ssh"
        self.cache = {}

    def get(self, addr, port=22, login="root", passwd=None, stdout=True, forward_agent=True,allow_agent=True, look_for_keys=True):
        key = "%s_%s_%s_%s" % (addr, port, login,j.data.hash.md5_string(str(passwd)))
        if key not in self.cache:
            self.cache[key] = SSHClient(addr, port, login, passwd, stdout=stdout, forward_agent=forward_agent,allow_agent=allow_agent,look_for_keys=look_for_keys)
        return self.cache[key]

    def removeFromCache(self, client):
        key = "%s_%s_%s_%s" % (client.addr, client.port, client.login,j.data.hash.md5_string(str(client.passwd)))
        client.close()
        if key in self.cache:
            self.cache.pop(key)

    def close(self):
        for key, client in self.cache.iteritems():
            client.close()

class SSHClient(object):

    def __init__(self, addr, port=22, login="root", passwd=None, stdout=True, forward_agent=True,allow_agent=True, look_for_keys=True,timeout=5.0):
        self.port = port
        self.addr = addr
        self.login = login
        self.passwd = passwd
        self.stdout = stdout
        if passwd!=None:
            self.forward_agent = False
            self.allow_agent=False
            self.look_for_keys=False
        else:
            self.forward_agent = forward_agent
            self.allow_agent=allow_agent
            self.look_for_keys=look_for_keys

        self._transport = None
        self._client = None
        self._cuisine = None


    def _test_local_agent(self):
        """
        try to connect to the local ssh-agent
        return True if local agent is running, False if not
        """
        agent = paramiko.Agent()
        if len(agent.get_keys()) == 0:
            return False
        else:
            return True

    @property
    def transport(self):
        # if self._transport is None:
            # self._transport = self.client.get_transport()
        self._transport = self.client.get_transport()
        return self._transport

    @property
    def client(self):
        if self._client is None:
            self._client = paramiko.SSHClient()
            self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            counter = 0
            while counter < 10:
                try:
                    self._client.connect(self.addr, self.port, username=self.login, password=self.passwd,allow_agent=self.allow_agent, look_for_keys=self.look_for_keys,timeout=1)
                    break
                except Exception as e:
                    counter += 0.1
                    if counter >= 10:
                        raise(e)
                    else:
                        time.sleep(0.1)
        return self._client

    def reset(self):
        self._client = None
        self._transport = None

    def getSFTP(self):
        sftp = self.client.open_sftp()
        return sftp

    def connectTest(self, cmd="ls /etc", timeout=3, die=True):
        """
        will trying to connect over ssh & execute the specified command, timeout is in sec
        error will be raised if not able to do (unless if die set)\
        return False if not ok
        """
        counter = 0

        rc = 1
        timeout1=j.data.time.getTimeEpoch()+timeout

        if j.sal.nettools.waitConnectionTest(self.addr, self.port, timeout)==False:
            print("Cannot connect to ssh server %s:%s"%(self.addr,self.port))
            return False

        while j.data.time.getTimeEpoch()<timeout1  and rc != 0:
            try:
                # print("connect ssh2.")
                rc, out = self.execute(cmd, showout=False)
                # print (rc)
            except (BadHostKeyException, AuthenticationException) as e:
                # cant' recover, no point to wait. exit now
                print(e)
                rc = 1                
                break
            except (SSHException, socket.error) as e:
                print(e)
                j.clients.ssh.removeFromCache(self)
                self._client = None
                self._transport = None
                time.sleep(0.1)
                continue

        if rc > 0:
            j.clients.ssh.removeFromCache(self)
            if die:
                j.events.opserror_critical("Could not connect to ssh on localhost on port %s" % self.port)
            else:
                return False
        return True

    def execute(self, cmd, showout=True, die=True, combinestdr=True):
        """
        run cmd & return
        return: (retcode,out_err)
        """
        ch = self.transport.open_session()
        ch.set_combine_stderr(combinestdr)
        if self.forward_agent:
            paramiko.agent.AgentRequestHandler(ch)

        ch.exec_command(cmd)
        buf = ''

        out = ch.recv(1024*1024).decode()
        while out:
            if showout and self.stdout:
                print(out)
            buf += out
            out = ch.recv(1024*1024).decode()

        retcode = ch.recv_exit_status()
        if die:
            if retcode > 0:
                raise RuntimeError("Cannot execute (ssh):\n%s\noutput:\n%s " % (cmd, buf))
        # print(buf)
        return (retcode, buf)

    def close(self):
        self.client.close()

    def rsync_up(self, source, dest, recursive=True):
        if dest[0] != "/":
            raise RuntimeError("dest path should be absolute, need / in beginning of dest path")

        dest = "%s@%s:%s" % (self.login, self.addr, dest)
        j.do.copyTree(source, dest, keepsymlinks=True, deletefirst=False,
                      overwriteFiles=True, ignoredir=[".egg-info", ".dist-info", "__pycache__"], ignorefiles=[".egg-info"], rsync=True,
                      ssh=True, sshport=self.port, recursive=recursive)

    def rsync_down(self, source, dest, source_prefix="", recursive=True):
        if source[0] != "/":
            raise RuntimeError("source path should be absolute, need / in beginning of source path")
        source = "%s@%s:%s" % (self.login, self.addr, source)
        j.do.copyTree(source, dest, keepsymlinks=True, deletefirst=False,
                      overwriteFiles=True, ignoredir=[".egg-info", ".dist-info"], ignorefiles=[".egg-info"], rsync=True,
                      ssh=True, sshport=self.port, recursive=recursive)

    @property
    def cuisine(self):
        if self._cuisine is None:
            executor = j.tools.executor.getSSHBased(self.addr, self.port, self.login, self.passwd)
            self._cuisine = executor.cuisine
        return self._cuisine

    def ssh_authorize(self, user, key):
        self.cuisine.ssh.authorize(user, key)
