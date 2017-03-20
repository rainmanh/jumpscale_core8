from JumpScale import j
import re

BASECMD = "btrfs"


class BtrfsExtensionFactory(object):

    def __init__(self):
        self.__jslocation__ = "j.sal.btrfs"

    def getBtrfs(self, executor=None):
        ex = executor if executor is not None else j.tools.executor.getLocal()
        return BtrfsExtension(ex)


class BtrfsExtension:

    def __init__(self, executor):
        self.__conspattern = re.compile("^(?P<key>[^:]+): total=(?P<total>[^,]+), used=(?P<used>.+)$", re.MULTILINE)
        self.__listpattern = re.compile("^ID (?P<id>\d+).+?path (?P<name>.+)$", re.MULTILINE)
        self._executor = executor
        self._disks = None
        self.logger = j.logger.get("btrfs.extension")

    @property
    def cuisine(self):
        return self._executor.cuisine

    def __btrfs(self, command, action, *args):
        cmd = "%s %s %s %s" % (BASECMD, command, action, " ".join(['"%s"' % a for a in args]))
        code, out, err = self._executor.execute(cmd, die=True, showout=False)

        # if code > 0:
        #     raise j.exceptions.RuntimeError(err)

        return out

    @property
    def disks(self):
        if self._disks == None:
            self._disks = self.cuisine.tools.diskmanager.getDisks()
        return self._disks

    def _snapshotCreate(self, path, dest, readonly=True):
        if readonly:
            self.__btrfs("subvolume", "snapshot -r", path, dest)
        else:
            self.__btrfs("subvolume", "snapshot", path, dest)

    def snapshotReadOnlyCreate(self, path, dest):
        """
        Create a readonly snapshot
        """
        self._snapshotCreate(path, dest, readonly=True)

    def snapshotRestore(self, path, dest, keep=True):
        """
        Restore snapshot located at path onto dest
        @param path: path of the snapshot to restore
        @param dest: location where to restore the snapshot
        @param keep: keep restored snapshot or not
        """
        self.subvolumeDelete(dest)
        self._snapshotCreate(path, dest, readonly=False)
        if not keep:
            self.subvolumeDelete(path)

    def subvolumeCreate(self, path):
        """
        Create a subvolume in path
        """
        if not self.subvolumeExists(path):
            self.__btrfs("subvolume", 'create', path)

    def subvolumeDelete(self, path):
        """
        full path to volume
        """
        if self.subvolumeExists(path):
            self.__btrfs("subvolume", "delete", path)

    def subvolumeExists(self, path):
        if not self._executor.cuisine.core.dir_exists(path):
            return False

        rc, res, err = self._executor.cuisine.core.run(
            "btrfs subvolume list %s" % path, checkok=False, die=False, showout=False)

        if rc > 0:
            if res.find("can't access") != -1:
                if self._executor.cuisine.core.dir_exists(path):
                    raise j.exceptions.RuntimeError(
                        "Path %s exists put is not btrfs subvolume, cannot continue." % path)
                else:
                    return False
            else:
                raise j.exceptions.RuntimeError("BUG:%s" % err)

        return True

    def subvolumeList(self, path, filter="", filterExclude=""):
        """
        List the snapshot/subvolume of a filesystem.
        """
        out = self.__btrfs("subvolume", "list", path)
        result = []
        for m in self.__listpattern.finditer(out):
            item = m.groupdict()
            # subpath=j.sal.fs.pathRemoveDirPart(item["name"].lstrip("/"),path.lstrip("/"))
            path2 = path + "/" + item["name"]
            path2 = path2.replace("//", "/")
            if item["name"].startswith("@"):
                continue
            if filter != "":
                if path2.find(filter) == -1:
                    continue
            if filterExclude != "":
                if path2.find(filterExclude) != -1:
                    continue
            result.append(path2)
        return result

    def subvolumesDelete(self, path, filter="", filterExclude=""):
        """
        delete all subvols starting from path
        filter e.g. /docker/
        """
        for i in range(4):
            # ugly for now, but cannot delete subvols, by doing this, it words brute force
            for path2 in self.subvolumeList(path, filter=filter, filterExclude=filterExclude):
                print("delete:%s" % path2)
                try:
                    self.subvolumeDelete(path2)
                except:
                    pass

    def storagePoolCreateOnAllNonRootDisks(self, path="/storage", redundant=False):
        """
        look for all disks which do not have a partition mounted on /
        and add them in btrfs storage pool
        if they are already mounted then just return
        """
        self.disks
        foundRoot = False
        res = []
        for disk in self.disks:
            found = False
            for partition in disk.partitions:
                if partition.mountpoint in ["/", "/tmp", "/home"]:
                    found = True
                    foundRoot = True
            if found == False:
                res.append(disk)
        if foundRoot == False:
            raise j.exceptions.Input(
                message="Did not find root disk, cannot create storage pool for btrfs on all other disks", level=1, source="", tags="", msgpub="")

        for disk in res:
            if disk.mountpoint == path:
                print("no need to format btrfs, was already done, warning: did not check if redundant")
                return
            disk.erase()

        disksLine = " ".join([item.name for item in res])
        if len(res) == 0:
            raise j.exceptions.Input(message="did not find disks to format", level=1, source="", tags="", msgpub="")
        if len(res) == 1:
            if redundant:
                raise j.exceptions.Input(
                    message="did only find 1 disk for btrfs and redundancy was asked for, cannot continue.", level=1, source="", tags="", msgpub="")
            cmd = "mkfs.btrfs -f %s" % disksLine
        elif len(res) == 2:
            cmd = "mkfs.btrfs -f -m raid1 -d raid1 %s" % disksLine
        else:
            cmd = "mkfs.btrfs -f -m raid10 -d raid10 %s" % disksLine

        self.logger.info(cmd)
        self._executor.execute(cmd)

        cmd = "mkdir -p %s;mount %s %s" % (path, res[0].name, path)
        self.logger.info(cmd)
        self._executor.execute(cmd)

        self.logger.info(self.getSpaceUsage(path))

        cmd = "btrfs filesystem show %s" % res[0].name
        rc, out, err = self._executor.execute(cmd)
        self.logger.info(out)

    def deviceAdd(self, path, dev):
        """
        Add a device to a filesystem.
        """
        self.__btrfs("device", 'add', dev, path)

    def deviceDelete(self, dev, path):
        """
        Remove a device from a filesystem.
        """
        self.__btrfs("device", 'delete', dev, path)

    def getSpaceUsage(self, path="/storage"):
        """
        return in MiB
        """
        out = self.__btrfs("filesystem", "df", path, "-b")

        result = {}
        for m in self.__conspattern.finditer(out):
            cons = m.groupdict()
            key = cons['key'].lower()
            key = key.replace(", ", "-")
            values = {'total': j.data.units.bytes.toSize(value=int(cons['total']), output='M'),
                      'used': j.data.units.bytes.toSize(value=int(cons['used']), output='M')}
            result[key] = values

        return result

    def getSpaceFree(self, path="/", percent=False):
        """
        @param percent: boolean, if true return percentage of free space, otherwise return free space in MiB
        @return free space
        """
        if not j.data.types.bool.check(percent):
            raise j.exceptions.Input('percent argument should be a boolean')

        res = self.getSpaceUsage(path)
        free = res['data-single']['total'] - res['data-single']['used']
        if percent:
            return "%.2f" % ((free / res["data-single"]["total"]) * 100)
        return free
