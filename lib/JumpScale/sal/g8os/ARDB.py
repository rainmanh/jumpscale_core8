from JumpScale import j
import io
import time

class ARDB:
    """ardb server"""

    def __init__(self, name, container, bind='0.0.0.0:16379', data_dir='/mnt/data', master=None):
        """
        TODO: write doc string
        """
        self.name = name
        self.master = master
        self.container = container
        self.bind = bind
        self.data_dir = data_dir
        self.master = None
        self._ays =None

    def _configure(self):
        buff = io.BytesIO()
        self.container.client.filesystem.download('/etc/ardb.conf', buff)
        content = buff.getvalue().decode()

        # update config
        content = content.replace('/mnt/data', self.data_dir)
        content = content.replace('0.0.0.0:16379', self.bind)

        if self.master is not None:
            content = content.replace('#slaveof 127.0.0.1:6379', 'slaveof {}'.format(self.master.bind))

        # make sure home directory exists
        self.container.client.filesystem.mkdir(self.data_dir)

        # upload new config
        self.container.client.filesystem.upload('/etc/ardb.conf.used', io.BytesIO(initial_bytes=content.encode()))

    def start(self,timeout=30):
        running, _ = self._container.is_running()
        if not running:
            self._container.start()

        self._configure()

        self.container.client.system('/bin/ardb-server /etc/ardb.conf.used')

        # wait for ardb to start
        start = time.time()
        end = start + timeout
        is_running, _ = self.is_running()
        while not is_running and time.time() < end:
            time.sleep(1)
            is_running, _ = self.is_running()

        if not is_running:
            raise RuntimeError("storage server {} didn't started")

    def stop(self, timeout=30):
        running, _ = self._container.is_running()
        if not running:
            return

        is_running, process = self.is_running()
        if is_running:
            self.container.client.process.kill(process['cmd']['id'])

            # wait for ardb to stop
            start = time.time()
            end = start + timeout
            is_running, _ = self.is_running()
            while is_running and time.time() < end:
                time.sleep(1)
                is_running, _ = self.is_running()

            if is_running:
                raise RuntimeError("storage server {} didn't stopped")

    def is_running(self):
        try:
            for process in self.container.client.process.list():
                if 'name' in process['cmd']['arguments'] and process['cmd']['arguments']['name'] == '/bin/ardb-server':
                    return (True, process)
            return (False, None)
        except Exception as err:
            if str(err).find("invalid container id"):
                return (False, None)
            raise

    @property
    def ays(self):
        if self._ays is None:
            from JumpScale.sal.g8os.atyourservice.StorageCluster import ARDBAys
            self._ays = ARDBAys(self)
        return self._ays
