from JumpScale import j
import os
from os.path import expanduser


class MockREDIS(object):

    def mock(self):
        j.sal.fs.changeDir(expanduser('~'))
        bin = os.path.join(expanduser('~'), 'redis')
        j.sal.fs.createDir(bin)
        j.do.pullGitRepo(url='https://git.aydo.com/binary/redis.git', dest=bin, login=None, passwd=None,
                         depth=1, ignorelocalchanges=False, reset=False, branch=None, revision=None)

        src = os.path.join(expanduser('~'), 'redis/redis')
        dst = j.sal.fs.joinPaths(j.dirs.baseDir, 'apps/redis')

        j.sal.fs.createDir(dst)
        j.sal.fs.symlink(src, dst, overwriteTarget=True)
        j.sal.fs.changeDir('%s/apps/redis' % j.dirs.baseDir)
        j.sal.process.execute('/opt/jumpscale8/apps/redis/redis-server', die=True, outputToStdout=True)

if __name__ == '__main__':
    MockREDIS().mock()
