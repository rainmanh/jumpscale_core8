from collections import defaultdict
import errno
import pwd
import grp
import os
import llfuse
from time import time
from llfuse import FUSEError

from JumpScale import j

try:
    import faulthandler
except ImportError:
    pass
else:
    faulthandler.enable()


class FuseOperations(llfuse.Operations):
    # {name: '', parent_inode: int, inode: int}
    contents = []
    # {inode: path}
    inode_path = {}

    def __init__(self, rootpath):
        super().__init__()
        self.rootpath = rootpath
        self._flistmeta = j.tools.flist.getFlistMetadata(rootpath)
        self.init_data()
        self.max_inode_count = llfuse.ROOT_INODE

    def init_data(self):
        self.inode_path[llfuse.ROOT_INODE] = self.rootpath
        content = {
            'name': '..',
            'parent_inode': llfuse.ROOT_INODE,
            'inode': llfuse.ROOT_INODE,
        }
        self.contents.append(content)

    def lookup(self, inode_p, name, ctx=None):
        if name == ".":
            inode = inode_p
        elif name == "..":
            inode = self._get_parent_inode(inode_p)
        else:
            for content in self.contents:
                if inode_p == content['parent_inode'] and name.decode("utf-8") == content['name']:
                    inode = content['inode']
                    break
        return self.getattr(inode, ctx)

    def getattr(self, inode, ctx=None):
        ppath = self.inode_path[inode]
        entity = self._flistmeta.getDirOrFile(ppath)
        entityAcl = self._flistmeta.aciCollection.get(entity['aclkey']).dbobj

        entry = llfuse.EntryAttributes()
        entry.st_ino = inode
        entry.generation = 0
        entry.entry_timeout = 300
        entry.attr_timeout = 300
        entry.st_mode = entityAcl.mode
        entry.st_uid = pwd.getpwnam(entityAcl.uname).pw_uid
        entry.st_gid = grp.getgrnam(entityAcl.gname).gr_gid
        entry.st_size = entity['size']

        entry.st_blksize = 4096

        entry.st_blocks = 0 if entity['size'] == 0 else int(((entity['size'] - 1) / entry.st_blksize + 1)) * 8
        entry.st_atime_ns = int(time() * 1e9)
        entry.st_mtime_ns = entity["modificationTime"] * 1e9
        entry.st_ctime_ns = entity["creationTime"] * 1e9

        return entry

    def opendir(self, inode, ctx):
        return inode

    def readdir(self, inode, off):
        entries = []
        ddir = self._flistmeta.getDirOrFile(self.inode_path[inode])

        # TODO: Refactor, Ugly
        for entry in ddir['dirs']:
            subdir = self._flistmeta.dirCollection.get(entry['key']).dbobj
            ppath = os.path.join(self.rootpath, subdir.location)
            if self.max_inode_count + 1 not in self.inode_path and ppath not in self.inode_path.values():
                self.max_inode_count += 1
                self.inode_path[self.max_inode_count] = os.path.join(self.rootpath, subdir.location)
                self.contents.append({
                    "inode": self.max_inode_count,
                    "parent_inode": inode,
                    "name": subdir.name
                })
            entries.append(entry)

        for entry in ddir['files']:
            ppath = os.path.join(self.rootpath, ddir['location'], entry['name'])
            if self.max_inode_count + 1 not in self.inode_path and ppath not in self.inode_path.values():
                self.max_inode_count += 1
                self.inode_path[self.max_inode_count] = os.path.join(self.rootpath, ddir['location'], entry['name'])
                self.contents.append({
                    "inode": self.max_inode_count,
                    "parent_inode": inode,
                    "name": entry['name']
                })
            entries.append(entry)

        for entry in ddir['links']:
            ppath = os.path.join(self.rootpath, ddir['location'], entry['name'])
            if self.max_inode_count + 1 not in self.inode_path and ppath not in self.inode_path.values():
                self.max_inode_count += 1
                self.inode_path[self.max_inode_count] = os.path.join(self.rootpath, ddir['location'], entry['name'])
                self.contents.append({
                    "inode": self.max_inode_count,
                    "parent_inode": inode,
                    "name": entry['name']
                })
            entries.append(entry)

        for entry in ddir['specials']:
            ppath = os.path.join(self.rootpath, ddir['location'], entry['name'])
            if self.max_inode_count + 1 not in self.inode_path and ppath not in self.inode_path.values():
                self.max_inode_count += 1
                self.inode_path[self.max_inode_count] = os.path.join(self.rootpath, ddir['location'], entry['name'])
                self.contents.append({
                    "inode": self.max_inode_count,
                    "parent_inode": inode,
                    "name": entry['name']
                })
            entries.append(entry)

        if off != 0 and off == len(entries):
            entries = []

        for idx, entry in enumerate(entries):
            for content in self.contents:
                if content['name'] == entry['name'] and content['parent_inode'] == inode:
                    entry_inode = content['inode']
            yield (bytes(entry['name'], 'utf-8'), self.getattr(entry_inode), idx + 1)

    def _get_parent_inode(self, inode):
        for content in self.contents:
            if inode == content['inode']:
                return content['parent_inode']

    def open(self, inode, flags, ctx):
        return inode

    def read(self, fh, offset, length):
        # FIXME: port to ardb
        import ipdb; ipdb.set_trace()
        data = self.get_row('SELECT data FROM inodes WHERE id=?', (fh,))[0]
        if data is None:
            data = b''
        return data[offset:offset+length]


class FuseExample(llfuse.Operations):
    def __init__(self, rootpath):
        MOUNT_POINT = '/tmp/mountpoint'
        ops = FuseOperations(rootpath)
        fuse_options = set(llfuse.default_options)
        fuse_options.add('fsname=testfs')
        fuse_options.discard('default_permissions')
        j.sal.fs.createDir(MOUNT_POINT)
        llfuse.init(ops, MOUNT_POINT, fuse_options)
        try:
            llfuse.main(workers=1)
        except:
            llfuse.close(unmount=False)
            raise
        llfuse.close()
