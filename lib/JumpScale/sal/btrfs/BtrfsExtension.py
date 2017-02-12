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

    def __btrfs(self, command, action, *args):
        cmd = "%s %s %s %s" % (BASECMD, command, action, " ".join(['"%s"' % a for a in args]))
        code, out, err = self._executor.execute(cmd, die=False, showout=False)

        if code > 0:
            raise j.exceptions.RuntimeError(err)

        return out

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

    def getSpaceUsage(self, path="/"):
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
