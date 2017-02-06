from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisinePortal(app):
    def _build_bin(self, root, repo='web_python'):
        url = 'git@git.aydo.com:binary/%s' % repo
        source = self.cuisine.development.git.pullRepo(
            url, depth=1, ssh=True,
        )

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
        for dir in ['macros', 'system', 'templates', 'wiki']:
            self.cuisine.core.file_copy(
                j.sal.fs.joinPaths(source, 'apps', 'portalbase', dir),
                j.sal.fs.joinPaths(root, 'apps', 'portals', 'portalbase'),
                recursive=True,
            )

        self.cuisine.core.file_copy(
            j.sal.fs.joinPaths(source, 'apps', 'portalbase', 'portal_start.py'),
            j.sal.fs.joinPaths(root, 'apps', 'portals', 'main'),
            recursive=True,
        )

        # copy portals
        for dir in ['base/AYS', 'base/Grid', 'base/system_*']:
            self.cuisine.core.file_copy(
                j.sal.fs.joinPaths(source, 'apps', 'gridportal', dir),
                j.sal.fs.joinPaths(root, 'apps', 'portals', 'main', 'base'),
                recursive=True,
            )

        # copy portal lib
        self.cuisine.core.file_copy(
            j.sal.fs.joinPaths(source, 'lib', 'portal'),
            j.sal.fs.joinPaths(root, 'lib', 'JumpScale'),
            recursive=True,
        )

    def _ensure_root(self, root):
        for directory in ['apps/portals/main/base', 'apps/portals/portalbase']:
            self.cuisine.core.dir_ensure(
                j.sal.fs.joinPaths(root, directory)
            )

    def build(self, root='/opt/jumpscale7', branch='master'):
        self._ensure_root(root)

        self._build_bin(root)

        url = 'git@github.com:jumpscale7/jumpscale_portal'
        source = self.cuisine.development.git.pullRepo(
            url, depth=1, branch=branch, ssh=True,
        )

        self._build_portal(source, root)
