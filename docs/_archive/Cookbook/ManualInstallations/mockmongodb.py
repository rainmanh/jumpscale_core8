from JumpScale import j


class MockMONGO(object):

    def mock(self):

        j.sal.fs.createDir('/opt/mongodb/bin')
        j.do.pullGitRepo(url='https://git.aydo.com/binary/influxdb_bin.git')

        src = '/opt/code/git/binary/mongodb/bin'
        dst = '/opt/mongodb/bin'
        j.sal.fs.symlink(src, dst, overwriteTarget=True)

        j.sal.fs.createDir("/optvar/var/mongodb/")
        j.sal.fs.changeDir('/opt/mongodb/bin')

        j.sal.process.execute(
            'rm -f /optvar/var/mongodb/main/mongod.lock;export LC_ALL=C;/opt/mongodb/bin/mongod --dbpath  /optvar/var/mongodb/ --smallfiles --rest --httpinterface', die=True, outputToStdout=True)

if __name__ == '__main__':
    MockMONGO().mock()
