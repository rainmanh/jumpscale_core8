from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisineOpenvcloud(app):
    def _build_libs(self, source, root):
        for dir in ['libs/CloudscalerLibcloud/CloudscalerLibcloud/*']:
            self.cuisine.core.file_copy(
                j.sal.fs.joinPaths(source, dir),
                j.sal.fs.joinPaths(root, 'libext'),
                recursive=True,
            )

        for dir in ['libs/agent-scripts/*']:
            self.cuisine.core.file_copy(
                j.sal.fs.joinPaths(source, dir),
                j.sal.fs.joinPaths(root, 'apps', 'agentcontroller', 'jumpscripts'),
                recursive=True,
            )

    def _build_apps(self, source, root):
        # portal
        self.cuisine.core.file_copy(
            j.sal.fs.joinPaths(source, 'apps', 'cbportal', '*'),
            j.sal.fs.joinPaths(root, 'apps', 'portals', 'main'),
            recursive=True,
        )

        # cloudbroker
        for dir in ['base', 'templates']:
            self.cuisine.core.file_copy(
                j.sal.fs.joinPaths(source, 'apps', 'cloudbroker', dir),
                j.sal.fs.joinPaths(root, 'apps', 'portals', 'main'),
                recursive=True,
            )

        # vfw
        for dir in ['base']:
            self.cuisine.core.file_copy(
                j.sal.fs.joinPaths(source, 'apps', 'vfw', dir),
                j.sal.fs.joinPaths(root, 'apps', 'portals', 'main'),
                recursive=True,
            )

        # cloudbrokerlib
        self.cuisine.core.file_copy(
            j.sal.fs.joinPaths(source, 'apps', 'cloudbroker', 'cloudbrokerlib'),
            j.sal.fs.joinPaths(root, 'libext'),
            recursive=True,
        )

        # other apps
        for dir in ['osis', 'libvirtlistener', 'routeros']:
            self.cuisine.core.file_copy(
                j.sal.fs.joinPaths(source, 'apps', dir),
                j.sal.fs.joinPaths(root, 'apps'),
                recursive=True,
            )

    def _build_routeros(self, root):
        url = 'git@git.aydo.com:binary/routeros'
        source = self.cuisine.development.git.pullRepo(
            url, depth=1, branch='2.1', ssh=True,
        )

        self.cuisine.core.file_copy(
            j.sal.fs.joinPaths(source, 'root', 'routeros-small-NETWORK-ID.qcow2'),
            j.sal.fs.joinPaths(root, 'apps', 'routeros', 'template'),
            recursive=True,
        )

    def build(self, root='/opt/jumpscale7', branch='master'):
        url = 'git@github.com:0-complexity/openvcloud'
        source = self.cuisine.development.git.pullRepo(
            url, depth=1, branch=branch, ssh=True,
        )

        self._build_libs(source, root)
        self._build_apps(source, root)
        self._build_routeros(root)
