from JumpScale import j

# class MountError(Exception):
#     pass


class Mount(object):
    def __init__(self,  device, path=None, options=''):
        self._device = device
        self._path = path
        self._autoClean = False
        if self._path is None:
            self._path = j.tools.path.get('/tmp').joinpath(j.data.idgenerator.generateXCharID(8))
            self._autoClean = True
        self._options = options

    @property
    def _mount(self):
        return 'mount {options} {device} {path}'.format(
            options='-o ' + self._options if self._options else '',
            device=self._device,
            path=self._path
        )

    @property
    def _umount(self):
        return 'umount {path}'.format(path=self._path)

    @property
    def path(self):
        return self._path

    def __enter__(self):
        return self.mount()

    def __exit__(self, type, value, traceback):
        return self.umount()

    def mount(self):
        """
        Mount partition
        """
        try:
            j.tools.path.get(self.path).makedirs()
            j.tools.executor.getLocal().execute(self._mount)
        except Exception as e:
            raise MountError(e)
        return self

    def umount(self):
        """
        Umount partition
        """
        try:
            j.tools.executor.getLocal().execute(self._unmount)
            if self._autoClean:
                j.tools.path.get(self.path).rmtree()
        except Exception as e:
            raise MountError(e)
        return self
