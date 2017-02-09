from JumpScale import j


class MountError(Exception):
    pass


class Mount:

    def __init__(self, device, path=None, options='', executor=None):
        self._device = device
        self._path = path
        self._autoClean = False
        if self._path is None:
            self._path = j.tools.path.get(
                '/tmp').joinpath(j.data.idgenerator.generateXCharID(8))
            self._autoClean = True
        self._options = options
        self._executor = executor or j.tools.executor.getLocal()

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
            self._executor.cuisine.core.dir_ensure(self.path)
            self._executor.execute(self._mount, showout=False)
        except Exception as e:
            raise MountError(e)
        return self

    def umount(self):
        """
        Umount partition
        """
        try:
            self._executor.execute(self._umount, showout=False)
            if self._autoClean:
                self._executor.cuisine.core.dir_remove(self.path)
        except Exception as e:
            raise MountError(e)
        return self
