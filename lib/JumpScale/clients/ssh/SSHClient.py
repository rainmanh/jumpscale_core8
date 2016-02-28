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

    def get(self, addr, port=22, login="root", passwd=None, stdout=True, forward_agent=True,allow_agent=True, look_for_keys=True,timeout=5,testConnection=False,die=True):
        key = "%s_%s_%s_%s" % (addr, port, login,j.data.hash.md5_string(str(passwd)))
        if key not in self.cache:
            self.cache[key] = SSHClient(addr, port, login, passwd, stdout=stdout, forward_agent=forward_agent,allow_agent=allow_agent,look_for_keys=look_for_keys,timeout=timeout)
        if testConnection:
            ret=self.cache[key].connectTest(timeout=timeout)
            if ret==False:
                if die:
                    raise RuntimeError("Cannot connect over ssh:%s %s"%(addr,port))
                else:
                    return False
            
        return self.cache[key]

    def removeFromCache(self, client):
        key = "%s_%s_%s_%s" % (client.addr, client.port, client.login,j.data.hash.md5_string(str(client.passwd)))
        client.close()
        if key in self.cache:
            self.cache.pop(key)

    def close(self):
        for key, client in self.cache.items():
            client.close()

class SSHClient(object):

    def __init__(self, addr, port=22, login="root", passwd=None, stdout=True, forward_agent=True,allow_agent=True, look_for_keys=True,timeout=5.0):
        self.port = port
        self.addr = addr
        self.login = login
        self.passwd = passwd
        self.stdout = stdout
        self._connection_ok = None
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
        if self.client is None:
            raise RuntimeError("Could not connect to %s:%s" % (self.addr, self.port))
        self._transport = self.client.get_transport()
        return self._transport

    @property
    def client(self):
        if self._client is None:
            print('ssh new client to %s@%s:%s' % (self.login, self.addr, self.port))

            start = j.data.time.getTimeEpoch()
            timeout = 20
            while start + timeout > j.data.time.getTimeEpoch():
                try:
                    self._client = paramiko.SSHClient()
                    self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    self._client.connect(self.addr, self.port, username=self.login, password=self.passwd,allow_agent=self.allow_agent, look_for_keys=self.look_for_keys, timeout=1)
                    break
                except:
                    self.reset()
                    time.sleep(1)
                    continue
            if self._client is None:
                raise RuntimeError('Impossible to create SSH connection to %s:%s' % (self.addr, self.port))

        return self._client

    def reset(self):
        self._client = None
        self._transport = None

    def getSFTP(self):
        sftp = self.client.open_sftp()
        return sftp

    def connectTest(self, cmd="ls /", timeout=5, die=True):
        """
        will trying to connect over ssh & execute the specified command, timeout is in sec
        error will be raised if not able to do (unless if die set)\
        return False if not ok
        """
        if not self._connection_ok:
            counter = 0

            rc = 1
            # timeout1=j.data.time.getTimeEpoch()+timeout
            start = j.data.time.getTimeEpoch()

            if j.sal.nettools.waitConnectionTest(self.addr, self.port, timeout)==False:
                print("Cannot connect to ssh server %s:%s"%(self.addr,self.port))
                return False

            while start + timeout > j.data.time.getTimeEpoch() and rc != 0:
                try:
                    rc, out = self.execute(cmd, showout=False)
                except (BadHostKeyException, AuthenticationException) as e:
                    # cant' recover, no point to wait. exit now
                    print("authentification error. abording connection")
                    print(e)
                    rc = 1
                    break
                except (SSHException, socket.error) as e:
                    print("authentification error. abording connection")
                    print(e)
                    j.clients.ssh.removeFromCache(self)
                    self._client.close()
                    self.reset()
                    time.sleep(0.1)
                    continue

            if rc > 0:
                j.clients.ssh.removeFromCache(self)
                self._connection_ok = False
                if die:
                    j.events.opserror_critical("Could not connect to ssh on %s@%s:%s" % (self.login, self.addr, self.port))
                return self._connection_ok
            self._connection_ok = True
        return self._connection_ok

    def execute(self, cmd, showout=True, die=True, combinestdr=True):
        """
        run cmd & return
        return: (retcode,out_err)
        """
        buff = ''
        retcode = 0

        ch = self.transport.open_session()

        if self.forward_agent:
            paramiko.agent.AgentRequestHandler(ch)

        ch.exec_command(cmd)
        stdout = ch.makefile('r')
        for line in stdout:
            buff += line
            if self.stdout and showout:
                print(line)

        retcode = ch.recv_exit_status()
        if retcode > 0:
            stderr = ch.makefile_stderr('r')
            errors = stderr.readlines()
            errors = ''.join(errors)
            if die:
                raise RuntimeError("Cannot execute (ssh):\n%s\noutput:\n%serrors:\n%s" % (cmd, buf,errors))
            else:
                buff = errors
        # print(buf)
        return (retcode, buff)

    def close(self):
        self.client.close()

    def rsync_up(self, source, dest, recursive=True):
        if dest[0] != "/":
            raise RuntimeError("dest path should be absolute, need / in beginning of dest path")

        dest = "%s@%s:%s" % (self.login, self.addr, dest)
        j.sal.fs.copyDirTree(source, dest, keepsymlinks=True, deletefirst=False,
                      overwriteFiles=True, ignoredir=[".egg-info", ".dist-info", "__pycache__"], ignorefiles=[".egg-info"], rsync=True,
                      ssh=True, sshport=self.port, recursive=recursive)

    def rsync_down(self, source, dest, source_prefix="", recursive=True):
        if source[0] != "/":
            raise RuntimeError("source path should be absolute, need / in beginning of source path")
        source = "%s@%s:%s" % (self.login, self.addr, source)
        j.sal.fs.copyDirTree(source, dest, keepsymlinks=True, deletefirst=False,
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
