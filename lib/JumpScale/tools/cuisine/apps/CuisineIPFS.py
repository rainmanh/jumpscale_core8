from JumpScale import j


app = j.tools.cuisine._getBaseAppClass()


class CuisineIPFS(app):
    NAME = "ipfs"

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def install(self, reset=False):
        "ipfsapi"

        if self._cuisine.platformtype.isLinux():
            url = "https://dist.ipfs.io/go-ipfs/v0.4.4/go-ipfs_v0.4.4_darwin-amd64.tar.gz"
        elif "darwin" in self._cuisine.platformtype.osname:
            url = "https://dist.ipfs.io/go-ipfs/v0.4.4/go-ipfs_v0.4.4_linux-amd64.tar.gz"

        path = j.do.download(url, overwrite=False)

        j.sal.fs.targzUncompress(path, j.dirs.tmpDir, "ipfs")

        cmd = j.sal.fs.joinPaths(j.dirs.tmpDir, "go-ips", "install.sh")

        self._cuisine.core.run(cmd)
