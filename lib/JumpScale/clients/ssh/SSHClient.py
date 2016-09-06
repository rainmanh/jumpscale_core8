from JumpScale import j

import paramiko
from paramiko.ssh_exception import SSHException, BadHostKeyException, AuthenticationException
import time
import socket

import threading
import queue


class SSHClientFactory:

    def __init__(self):
        self.__jslocation__ = "j.clients.ssh"
        self.logger = j.logger.get("j.clients.ssh")
        self.cache = {}

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
        rc, out, err = j.tools.cuisine.local.run("ssh-add -L", die=False)
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


class SSHClient:

    def __init__(self, addr='', port=22, login="root", passwd=None, usesproxy=False, stdout=True, forward_agent=True, allow_agent=True,
                 look_for_keys=True, key_filename=None, passphrase=None, timeout=5.0):
        self.port = port
        self.addr = addr
        self.login = login
        self.passwd = passwd
        self.stdout = stdout
        self.timeout = timeout
        if passwd is not None:
            self.forward_agent = False
            self.allow_agent = False
            self.look_for_keys = False
            self.key_filename = None
            self.passphrase = None
        else:
            self.forward_agent = forward_agent
            self.allow_agent = allow_agent
            self.look_for_keys = look_for_keys
            self.key_filename = key_filename
            self.passphrase = passphrase

        self.logger = j.logger.get("j.clients.ssh")

        self._transport = None
        self._client = None
        self._cuisine = None
        self.usesproxy = usesproxy

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

    def connectViaProxy(self, host, username, port, identityfile, proxycommand=None):
        self.usesproxy = True
        client = paramiko.SSHClient()
        client._policy = paramiko.WarningPolicy()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        import os.path
        self.host = host
        cfg = {'hostname': host, 'username': username, "port": port}
        self.addr = host
        self.user = username

        if identityfile is not None:
            cfg['key_filename'] = identityfile
            self.key_filename = cfg['key_filename']

        if proxycommand is not None:
            cfg['sock'] = paramiko.ProxyCommand(proxycommand)
        cfg['timeout'] = 5
        cfg['allow_agent'] = True
        cfg['banner_timeout'] = 5
        self.cfg = cfg
        self.forward_agent = True
        self._client = client
        self._client.connect(**cfg)

        return self._client
    @property
    def transport(self):
        if self.client is None:
            raise j.exceptions.RuntimeError(
                "Could not connect to %s:%s" % (self.addr, self.port))
        return self.client.get_transport()

    @property
    def client(self):
        if self._client is None:
            self.logger.info("Test connection to %s:%s:%s" %
                             (self.addr, self.port, self.login))
            start = j.data.time.getTimeEpoch()

            if j.sal.nettools.waitConnectionTest(self.addr, self.port, self.timeout) is False:
                self.logger.error("Cannot connect to ssh server %s:%s with login:%s and using sshkey:%s" % (
                    self.addr, self.port, self.login, self.key_filename))
                return None
            start = j.data.time.getTimeEpoch()
            while start + self.timeout > j.data.time.getTimeEpoch():
                j.tools.console.hideOutput()
                try:
                    self._client = paramiko.SSHClient()
                    self._client.set_missing_host_key_policy(
                        paramiko.AutoAddPolicy())
                    self.pkey = None
                    if self.key_filename:
                        # self.allow_agent = False
                        self.look_for_keys = False
                        self.pkey = paramiko.RSAKey.from_private_key_file(
                            self.key_filename, password=self.passphrase)
                        if not j.do.checkSSHAgentAvailable():
                            j.do._.loadSSHAgent()
                        if not j.do.getSSHKeyPathFromAgent(self.key_filename, die=False):
                            j.do.loadSSHKeys(self.key_filename)
                    self._client.connect(self.addr, self.port, username=self.login, password=self.passwd,
                                         pkey=self.pkey, allow_agent=self.allow_agent, look_for_keys=self.look_for_keys,
                                         timeout=2.0, banner_timeout=3.0)
                    break
                except (BadHostKeyException, AuthenticationException) as e:
                    self.logger.error(
                        "Authentification error. Aborting connection")
                    self.logger.error(e)
                    raise j.exceptions.RuntimeError(str(e))

                except (SSHException, socket.error) as e:
                    self.logger.error(
                        "Unexpected error in socket connection for ssh. Aborting connection and try again.")
                    self.logger.error(e)
                    self._client.close()
                    self.reset()
                    time.sleep(1)
                    continue
                except Exception as e:
                    j.clients.ssh.removeFromCache(self)
                    msg = "Could not connect to ssh on %s@%s:%s. Error was: %s" % (
                        self.login, self.addr, self.port, e)
                    raise j.exceptions.RuntimeError(msg)
            if self._client is None:
                raise j.exceptions.RuntimeError(
                    'Impossible to create SSH connection to %s:%s' % (self.addr, self.port))

        return self._client

    def reset(self):
        if self._client is not None:
            self._client = None
        # self._transport = None

    def getSFTP(self):
        sftp = self.client.open_sftp()
        return sftp

    def execute(self, cmd, showout=True, die=True):
        """
        run cmd & return
        return: (retcode,out_err)
        """
        ch = self.transport.open_session()
        if self.forward_agent:
            paramiko.agent.AgentRequestHandler(ch)
        class StreamReader(threading.Thread):

            def __init__(self, stream, queue, flag):
                super(StreamReader, self).__init__()
                self.stream = stream
                self.queue = queue
                self.flag = flag
                self._stopped = False
                self.setDaemon(True)

            def run(self):
                """
                read until all buffers are empty and retrun code is ready
                """
                while not self.stream.closed and not self._stopped:
                    buf = ''
                    buf = self.stream.readline()
                    if len(buf) > 0:
                        self.queue.put((self.flag, buf))
                    elif not ch.exit_status_ready():
                        continue
                    elif self.flag == 'O' and ch.recv_ready():
                        continue
                    elif self.flag == 'E' and ch.recv_stderr_ready():
                        continue
                    else:
                        break
                self.queue.put(('T', self.flag))

        # execute the command on the remote server
        ch.exec_command(cmd)
        # indicate that we're not going to write to that channel anymore
        ch.shutdown_write()
        # create file like object for stdout and stderr to read output of
        # command
        stdout = ch.makefile('r')
        stderr = ch.makefile_stderr('r')

        # Start stream reader thread that will read strout and strerr
        inp = queue.Queue()
        outReader = StreamReader(stdout, inp, 'O')
        errReader = StreamReader(stderr, inp, 'E')
        outReader.start()
        errReader.start()

        err = ""  # error buffer
        out = ""  # stdout buffer
        out_eof = False
        err_eof = False

        while out_eof is False or err_eof is False:
            try:
                chan, line = inp.get(block=True, timeout=1.0)
                if chan == 'T':
                    if line == 'O':
                        out_eof = True
                    elif line == 'E':
                        err_eof = True
                    continue
                line = j.data.text.toAscii(line)
                if chan == 'O':
                    if showout:
                        print(line.rstrip())
                        # print((line.strip()))
                    out += line
                elif chan == 'E':
                    if showout:
                        print(line.rstrip())
                        # print((line.strip()))
                    err += line
            except queue.Empty:
                pass

        # stop the StreamReader and wait for the thread to finish
        outReader._stopped = True
        errReader._stopped = True
        outReader.join()
        errReader.join()

        # indicate that we're not going to read from this channel anymore
        ch.shutdown_read()
        # close the channel
        ch.close()

        # close all the pseudofiles
        stdout.close()
        stderr.close()

        rc = ch.recv_exit_status()

        if rc and die:
            raise j.exceptions.RuntimeError(
                "Cannot execute (ssh):\n%s\noutput:\n%serrors:\n%s" % (cmd, out, err))

        # if err:
        #     self.logger.error(err)
        return rc, out, err

    def close(self):
        if self.client is not None:
            self.client.close()

    def rsync_up(self, source, dest, recursive=True):
        if dest[0] != "/":
            raise j.exceptions.RuntimeError(
                "dest path should be absolute, need / in beginning of dest path")

        dest = "%s@%s:%s" % (self.login, self.addr, dest)
        j.sal.fs.copyDirTree(source, dest, keepsymlinks=True, deletefirst=False,
                             overwriteFiles=True, ignoredir=[".egg-info", ".dist-info", "__pycache__"], ignorefiles=[".egg-info"], rsync=True,
                             ssh=True, sshport=self.port, recursive=recursive)

    def rsync_down(self, source, dest, source_prefix="", recursive=True):
        if source[0] != "/":
            raise j.exceptions.RuntimeError(
                "source path should be absolute, need / in beginning of source path")
        source = "%s@%s:%s" % (self.login, self.addr, source)
        j.sal.fs.copyDirTree(source, dest, keepsymlinks=True, deletefirst=False,
                             overwriteFiles=True, ignoredir=[".egg-info", ".dist-info"], ignorefiles=[".egg-info"], rsync=True,
                             ssh=True, sshport=self.port, recursive=recursive)

    @property
    def cuisine(self):
        if not self.usesproxy and self._cuisine is None:
            executor = j.tools.executor.getSSHBased(self.addr, self.port, self.login, self.passwd)
            self._cuisine = executor.cuisine
        if self.usesproxy:
            ex = j.tools.executor.getSSHViaProxy(self.host)
            self._cuisine = j.tools.cuisine.get(self)
        return self._cuisine

    def ssh_authorize(self, user, key):
        self.cuisine.ssh.authorize(user, key)
