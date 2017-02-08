import asyncio
import asyncssh
import sys
from io import StringIO
import functools
from JumpScale import j


class SSHClientSession(asyncssh.SSHClientSession):

    def __init__(self, showout):
        self.logger = j.logger.get('j.client.asyncssh')
        self._showout = showout
        self.exit_status = None
        self._stdout_buf = StringIO()
        self._stderr_buf = StringIO()

    @property
    def stdout(self):
        return self._stdout_buf.getvalue()

    @property
    def stderr(self):
        return self._stderr_buf.getvalue()

    """
    Callbacks
    """

    def data_received(self, data, datatype):
        if datatype == asyncssh.EXTENDED_DATA_STDERR:
            self._stderr_buf.write(data)
            if self._showout:
                print(data, end='', file=sys.stderr)
        else:
            self._stdout_buf.write(data)
            if self._showout:
                print(data, end='')

    def exit_status_received(self, status):
        self.exit_status = status

    def connection_lost(self, exc):
        if exc:
            self.logger.error('SSH session error: ' + str(exc))


class SSHClient(asyncssh.SSHClient):

    def __init__(self):
        self.logger = j.logger.get('j.client.asyncssh')
        self.conn = None

    def connection_made(self, conn):
        self.logger.debug('Connection made to %s.' % conn.get_extra_info('peername')[0])
        self.conn = conn

    def connection_lost(self, exc):
        if exc:
            self.logger.error('SSH connction error: ' + str(exc))
        self.conn = None

    def auth_completed(self):
        self.logger.debug('Authentication successful.')


class AsyncSSHClient:

    def __init__(self, addr='', port=22, login="root", passwd=None, usesproxy=False, forward_agent=True, allow_agent=True,
                 look_for_keys=True, key_filename=(), passphrase=None, timeout=5.0):
        self.addr = addr
        self.port = port
        self.login = login
        self.password = passwd
        self.timeout = timeout
        self.allow_agent = allow_agent
        self.forward_agent = forward_agent
        self.look_for_keys = look_for_keys
        self.key_filename = key_filename or ()
        self.passphrase = passphrase
        self.logger = j.logger.get("j.clients.ssh")

        self._client = None

    # def connected(self):
    #     return self._client is not None and self._client.conn is not None

    async def run_command(self, cmd, showout=True, die=True, env={}):
        if self._client is None or self._client.conn is None:
            self.logger.debug("create new connection to {}:{}".format(self.addr, self.port))

            try:
                _, self._client = await asyncio.wait_for(
                    asyncssh.create_connection(
                        client_factory=SSHClient,
                        host=self.addr,
                        username=self.login,
                        password=self.password,
                        known_hosts=None,
                        agent_forwarding=self.forward_agent,
                        client_keys=list(self.key_filename),
                        passphrase=self.passphrase),
                    timeout=self.timeout)
            except asyncio.TimeoutError as ex:
                self.logger.error("connection to {}:{} timed out".format(self.addr, self.port))
                raise ex

        chan, session = await self._client.conn.create_session(
            session_factory=functools.partial(SSHClientSession, showout=showout),
            command=cmd,
            env=env)
        await chan.wait_closed()

        return session.exit_status, session.stdout, session.stderr

    async def execute(self, cmd, showout=True, die=True):
        try:
            rc, out, err = await self.run_command(
                cmd=cmd,
                showout=showout,
                die=die)
            return rc, out, err
        except (OSError, asyncssh.Error) as exc:
            self.logger.error('SSH connection failed: ' + str(exc))
            raise

    def close(self):
        """
        Cleanly close the SSH connection
        """
        if self._client and self._client.conn:
            self._client.conn.close()
            self.client = None

if __name__ == '__main__':
    client = AsyncSSHClient(addr='localhost', port=22, login="root", passwd='rooter')
    loop = asyncio.get_event_loop()
    rc, out, err = loop.run_until_complete(client.execute('ls /'))
    # rc, out, err = client.execute('ls /')
    from IPython import embed
    embed()
