from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisineRestic(app):

    NAME = 'restic'

    def _init(self):
        self.BUILDDIR = self.core.replace("$BUILDDIR/restic")
        self.CODEDIR = self.core.replace("$GOPATHDIR/src/github.com/restic/restic")

    def reset(self):
        """
        helper method to clean what this module generates.
        """
        super().reset()
        self.core.dir_remove(self.BUILDDIR)
        self.core.dir_remove(self.CODEDIR)

    def build(self, install=True, reset=False):
        if reset is False and (self.isInstalled() or self.doneGet('build')):
            return

        if reset:
            self.reset()

        self.cuisine.development.golang.install()

        # build
        url = "https://github.com/restic/restic/"
        self.cuisine.development.git.pullRepo(url, dest=self.CODEDIR, ssh=False, depth=1)

        build_cmd = 'cd {dir}; go run build.go -k -v'.format(dir=self.CODEDIR)
        self.cuisine.core.run(build_cmd, profile=True)

        self.doneSet("build")

        if install:
            self.install()

    def install(self,reset=False):
        """
        download, install, move files to appropriate places, and create relavent configs
        """

        if self.doneGet("install") and not reset:
            return

        self.cuisine.core.file_copy(self.CODEDIR+'/restic', '$BINDIR')

        self.doneSet("install")


    def initRepository(self, path, password):
        """
        @param path: where to create the backup repository
        @param password: password to set on the repository
        """
        env = {
            'RESTIC_REPOSITORY': path,
            'RESTIC_PASSWORD': password
        }
        cmd = '$BINDIR/restic init'
        self.cuisine.core.run(cmd, env=env)

    def snapshot(self, path, repo, password, tag=None):
        """
        @param path: directory/file to snapshot
        @param repo: restic repository where to create the snapshot
        @param password: password to use to unlock the restic repository
        """
        env = {
            'RESTIC_REPOSITORY': repo,
            'RESTIC_PASSWORD': password
        }
        cmd = '$BINDIR/restic backup {} '.format(path)
        if tag:
            cmd += " --tag {}".format(tag)
        self.cuisine.core.run(cmd, env=env)

    def restore_snapshot(self, snapshot_id, dest, repo, password):
        """
        @param snapshot_id: id of the snapshot to restore
        @param dest: path where to restore the snapshot to
        @param repo: restic repository where to create the snapshot
        @param password: password to use to unlock the restic repository
        """
        env = {
            'RESTIC_REPOSITORY': repo,
            'RESTIC_PASSWORD': password
        }
        cmd = '$BINDIR/restic restore --target {dest} {id} '.format(dest=dest, id=snapshot_id)
        self.cuisine.core.run(cmd, env=env)

    def _chunk(self, line):
        word = ''
        for c in line:
            if c == ' ':
                if word:
                    yield word
                    word = ''
                continue
            else:
                word += c
        if word:
            yield word

    def list_snapshots(self, repo, password):
        """
        @param repo: restic repository where to create the snapshot
        @param password: password to use to unlock the restic repository
        @return: list of dict representing a snapshot
        { 'date': '2017-01-17 16:15:28',
          'directory': '/optvar/cfg',
          'host': 'myhost',
          'id': 'ec853b5d',
          'tags': 'backup1'
        }
        """
        env = {
            'RESTIC_REPOSITORY': repo,
            'RESTIC_PASSWORD': password
        }
        cmd = '$BINDIR/restic snapshots'
        _, out, _ = self.cuisine.core.run(cmd, env=env)

        snapshots = []
        for line in out.splitlines()[2:]:
            ss = list(self._chunk(line))

            snapshot = {
                'id': ss[0],
                'date': ' '.join(ss[1:3]),
                'host': ss[3]
            }
            if len(ss) == 6:
                snapshot['tags'] = ss[4]
                snapshot['directory'] = ss[5]
            else:
                snapshot['tags'] = ''
                snapshot['directory'] = ss[4]
            snapshots.append(snapshot)

        return snapshots

    def check_repo_integrity(self, repo, password):
        """
        @param repo: restic repository where to create the snapshot
        @param password: password to use to unlock the restic repository
        @return: True if integrity is ok else False
        """
        env = {
            'RESTIC_REPOSITORY': repo,
            'RESTIC_PASSWORD': password
        }
        cmd = '$BINDIR/restic check'
        rc, _, _ = self.cuisine.core.run(cmd, env=env, die=False)
        if rc != 0:
            return False
        return True
