from JumpScale import j
import re

BASECMD = "btrfs"

KB = 1024
MB = KB * 1024
GB = MB * 1024
TB = GB * 1024
Ki = 1024
Mi = Ki * 1024
Gi = Mi * 1024
Ti = Gi * 1024

FACTOR = {
    None: 1,
    '':   1,
    'KB': KB,
    'MB': MB,
    'GB': GB,
    'TB': TB,
    'KI': Ki,
    'MI': Mi,
    'GI': Gi,
    'TI': Ti
}

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
        code, out, err = self._executor.execute(cmd, die=False)

        if code > 0:
            raise j.exceptions.RuntimeError(err)

        return out

    def snapshotReadOnlyCreate(self, path, dest):
        """
        Create a readonly snapshot
        """
        self.__btrfs("subvolume", "snapshot -r", path, dest)

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

        rc, res, err = self._executor.execute(
            "btrfs subvolume list %s" % path, checkok=False, die=False)

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

    def __consumption2kb(self, word):
        m = re.match("(\d+.\d+)(\D{2})?", word)
        if not m:
            raise ValueError(
                "Invalid input '%s' should be in the form of 0.00XX" % word)

        if m.group(2) is None:
            mm = ""
        else:
            mm = m.group(2).upper()

        value = float(m.group(1)) * FACTOR[mm]
        return value / 1024 / 1024

    def getSpaceUsage(self, path="/"):
        """
        return in mbytes
        """
        out = self.__btrfs("filesystem", "df", path)

        result = {}
        for m in self.__conspattern.finditer(out):
            cons = m.groupdict()
            key = cons['key'].lower()
            key = key.replace(", ", "-")
            values = {'total': self.__consumption2kb(cons['total']),
                      'used': self.__consumption2kb(cons['used'])}
            result[key] = values

        return result

    def getSpaceUsageData(self, path="/"):
        """
        @return total/used (mbytes)
        """
        res = self.getSpaceUsage(path)
        return (int(res["data-single"]["total"]), int(res["data-single"]["used"]))

    def getSpaceUsageDataFree(self, path="/"):
        """
        @return percent as int
        """
        res = self.getSpaceUsage(path)
        return int(res["data-single"]["used"] / res["data-single"]["total"] * 100)
