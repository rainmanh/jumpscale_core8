from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisinePortal(app):
    def _build_bin(self, root, repo='web_python'):
        url = 'http://git.aydo.com/binary/%s' % repo
        source = self.cuisine.development.git.pullRepo(url, depth=1)

        self.cuisine.core.file_copy(
            j.sal.fs.joinPaths(source, 'root', 'jslib'),
            j.sal.fs.joinPaths(root, 'apps', 'portals'),
            recursive=True,
        )

        self.cuisine.core.file_copy(
            j.sal.fs.joinPaths(source, 'root', 'lib', '*'),
            j.sal.fs.joinPaths(root, 'libext'),
            recursive=True,
        )

    def _build_portal(self, source, root):
        # copy portal base
        self.cuisine.core.file_copy(
            j.sal.fs.joinPaths(source, 'apps', 'portalbase'),
            j.sal.fs.joinPaths(root, 'apps', 'portals'),
            recursive=True,
        )

        # copy portal lib
        self.cuisine.core.file_copy(
            j.sal.fs.joinPaths(source, 'lib', 'portal'),
            j.sal.fs.joinPaths(root, 'lib', 'JumpScale'),
            recursive=True,
        )

    def build(self, root='/opt/jumpscale7', branch='master'):
        self.cuisine.core.dir_ensure(
            j.sal.fs.joinPaths(root, 'apps', 'portals')
        )

        self._build_bin(root)

        url = 'https://github.com/jumpscale7/jumpscale_portal'
        source = self.cuisine.development.git.pullRepo(
            url, depth=1, branch=branch
        )

        self._build_portal(source, root)
