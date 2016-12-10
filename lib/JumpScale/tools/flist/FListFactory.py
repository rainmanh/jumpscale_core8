from JumpScale import j
from stat import *
import brotli
import hashlib
import functools
import subprocess
import pwd
import grp
import os
import sys
import re

import capnp
from JumpScale.tools.flist import model_capnp as ModelCapnp

from JumpScale.tools.flist.models import DirModel
from JumpScale.tools.flist.models import DirCollection
from JumpScale.tools.flist.models import ACIModel
from JumpScale.tools.flist.models import ACICollection

from JumpScale.tools.flist.FList import FList


class FListFactory(object):

    def __init__(self):
        self.__jslocation__ = "j.tools.flist"

    def getCapnpSchema(self):
        return ModelCapnp

    def getDirCollectionFromDB(self, name="test", kvs=None):
        """
        std keyvalue stor is redis used by core
        use a name for each flist because can be cached & stored in right key value stor
        """
        schema = self.getCapnpSchema()

        # now default is mem, if we want redis as default store uncomment next, but leave for now, think mem here ok
        # if kvs == None:
        #     kvs = j.servers.kvs.getRedisStore(name="flist", unixsocket="%s/redis.sock" % j.dirs.tmpDir)

        collection = j.data.capnp.getModelCollection(
            schema.Dir, category="flist_%s" % name, modelBaseClass=DirModel.DirModel,
            modelBaseCollectionClass=DirCollection.DirCollection, db=kvs, indexDb=kvs)
        return collection

    def getACICollectionFromDB(self, name="test", kvs=None):
        """
        if kvs None then mem will be used

        """
        schema = self.getCapnpSchema()

        collection = j.data.capnp.getModelCollection(
            schema.ACI, category="ACI_%s" % name, modelBaseClass=ACIModel.ACIModel,
            modelBaseCollectionClass=ACICollection.ACICollection, db=kvs, indexDb=kvs)
        return collection

    def getUserGroupCollectionFromDB(self, name="usergroup", kvs=None):
        """
        if kvs None then mem will be used
        """
        schema = self.getCapnpSchema()

        collection = j.data.capnp.getModelCollection(
            schema.UserGroup, category="ug_%s" % name, modelBaseClass=ACIModel.ACIModel,
            modelBaseCollectionClass=ACICollection.ACICollection, db=kvs, indexDb=kvs)
        return collection

    def getFlist(self, rootpath="/", namespace="main", kvs=None):
        """
        @param namespace, this normally is some name you cannot guess, important otherwise no security
        Return a Flist object
        """
        dirCollection = self.getDirCollectionFromDB(name="dir_%s" % namespace, kvs=kvs)
        aciCollection = self.getACICollectionFromDB(name="aci_%s" % namespace, kvs=kvs)
        userGroupCollection = self.getUserGroupCollectionFromDB(name="ug_%s" % namespace, kvs=kvs)
        return FList(rootpath=rootpath, namespace=namespace, dirCollection=dirCollection, aciCollection=aciCollection, userGroupCollection=userGroupCollection)

    def get_archiver(self):
        """
        Return a FListArchiver object

        This is used to push flist to IPFS
        """
        return FListArchiver()

    def test(self):
        testDir = "/JS8/opt/"
        flist = self.getFlist(rootpath=testDir)
        flist.add(testDir)

        def pprint(path, ddir, name):
            print(path)

        flist.walk(fileFunction=pprint, dirFunction=pprint, specialFunction=pprint, linkFunction=pprint)


class FListArchiver:
    # This is a not efficient way, the only other possibility
    # is to call brotli binary to compress big file if needed
    # currently, this in-memory way is used

    def __init__(self, ipfs_cfgdir=None):
        cl = j.tools.cuisine.local
        self._ipfs = cl.core.command_location('ipfs')
        if not ipfs_cfgdir:
            self._env = 'IPFS_PATH=%s' % cl.core.args_replace('$cfgDir/ipfs/main')
        else:
            self._env = 'IPFS_PATH=%s' % ipfs_cfgdir

    def _compress(self, source, destination):
        with open(source, 'rb') as content_file:
            content = content_file.read()

        compressed = brotli.compress(content, quality=6)

        with open(destination, "wb") as output:
            output.write(compressed)

    def push_to_ipfs(self, source):
        cmd = "%s %s add '%s'" % (self._env, self._ipfs, source)
        out = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)

        m = re.match(r'^added (.+) (.+)$', out.stdout.decode())
        if m is None:
            raise RuntimeError('invalid output from ipfs add: %s' % out)

        return m.group(1)

    def build(self, flist, backend):
        hashes = flist.getHashList()

        if not os.path.exists(backend):
            os.makedirs(backend)

        for hash in hashes:
            files = flist.filesFromHash(hash)

            # skipping non regular files
            if not flist.isRegular(files[0]):
                continue

            print("Processing: %s" % hash)

            root = "%s/%s/%s" % (backend, hash[0:2], hash[2:4])
            file = hash

            target = "%s/%s" % (root, file)

            if not os.path.exists(root):
                os.makedirs(root)

            # compressing the file
            self._compress(files[0], target)

            # adding it to ipfs network
            hash = self.push_to_ipfs(target)
            print("Network hash: %s" % hash)

            # updating flist hash with ipfs hash
            for f in files:
                flist.setHash(f, hash)

        print("Files compressed and shared")