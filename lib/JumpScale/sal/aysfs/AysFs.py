#!/usr/bin/env python
from JumpScale import j
import os

from sal.base.SALObject import SALObject


class AysFsFactory(object):

    def __init__(self):
        self.__jslocation__ = "j.sal.aysfs"

    def get(self, cuisine=None):
        return AysFs(cuisine=cuisine)

    def _getFlist(self, name):
        if not j.sal.fs.exists('/aysfs/flist/'):
            j.sal.fs.createDir('/aysfs/flist/')

        flist = '/aysfs/flist/%s.flist' % name
        if not j.sal.fs.exists(flist):
            print('[+] downloading flist: %s' % name)
            storx = j.clients.storx.get('https://stor.jumpscale.org/storx')
            storx.getStaticFile('%s.flist' % name, flist)

    def getJumpscale(self, cuisine=None):
        self._getFlist('js8_opt')

        js8opt = AysFs('jumpscale', cuisine)
        js8opt.setUnique()
        js8opt.addMount('/aysfs/docker/jumpscale', 'RO', '/aysfs/flist/js8_opt.flist', prefix='/opt')
        js8opt.addBackend('/ays/backend/jumpscale', 'js8_opt')
        js8opt.addStor()
        return js8opt

    def getOptvar(self, cuisine=None):
        self._getFlist('js8_optvar')

        js8optvar = AysFs('optvar', cuisine)
        js8optvar.addMount('/aysfs/docker/$NAME', 'OL', '/aysfs/flist/js8_optvar.flist', prefix='/optvar')
        js8optvar.addBackend('/ays/backend/$NAME', 'js8_optvar')
        js8optvar.addStor()
        return js8optvar


class AysFs(SALObject):

    def __init__(self, name, cuisine=None):
        self.cuisine = cuisine
        if self.cuisine is None:
            self.cuisine = j.tools.cuisine.local

        self.mounts = []
        self.backends = []
        self.stors = []

        self.root = '/aysfs'
        self.name = name.replace('/', '-')
        self.unique = False
        self.tmux = j.sal.tmux.get(self.cuisine, self.cuisine.executor)

        self.defstor = 'https://stor.jumpscale.org/storx'

    def setRoot(self, root):
        self.root = root

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name.replace('/', '-')

    def setUnique(self, value=True):
        self.unique = value

    def isUnique(self):
        return self.unique

    def getPrefixs(self):
        prefixs = {}

        for mount in self.mounts:
            source = '%s/%s' % (mount['path'], mount['prefix'])
            prefixs[source] = mount['prefix']

        return prefixs

    def addMount(self, path, mode, flist=None, backend='default', prefix=''):
        mount = {
            'path': path,
            'backend': backend,
            'mode': mode,
            'prefix': prefix
        }

        if flist:
            mount['flist'] = flist

        self.mounts.append(mount)

        return True

    def addBackend(self, path, namespace, stor='default', name='default'):
        backend = {
            'name': name,
            'path': path,
            'stor': stor,
            'namespace': namespace,
            'encrypted': False,                # FIXME
            'aydostor_push_cron': '@every 10s'  # FIXME
        }

        self.backends.append(backend)

        return True

    def addStor(self, remote=None, username='', password='', name='default'):
        stor = {
            'name': name,
            'addr': remote if remote else self.defstor,
            'login': username,
            'passwd': password
        }

        self.stors.append(stor)

        return True

    def _generate(self, items):
        build = {}

        # extract name from item and use it as key
        for item in items:
            temp = item.copy()
            temp.pop('name', None)

            build[item['name']] = temp

        return build

    def _clean(self, items):
        output = []

        for item in items:
            temp = item.copy()
            temp.pop('prefix', None)

            output.append(temp)

        return output

    def _parse(self, items):
        for item in items:
            if item.get('path'):
                item['path'] = item['path'].replace('$NAME', self.name)

        return items

    def generate(self):
        config = {
            'mount': self._clean(self.mounts),
            'backend': self._generate(self.backends),
            'aydostor': self._generate(self.stors)
        }

        return j.data.serializer.toml.dumps(config)

    def unmount(self, path):
        self.cuisine.run('umount %s; exit 0' % path)

    def _ensure_path(self, path):
        if not j.sal.fs.exists(path):
            j.sal.fs.createDir(path)

    def _install(self):
        self._ensure_path(self.root)
        self._ensure_path('%s/etc' % self.root)
        self._ensure_path('%s/bin' % self.root)

        binary = '%s/bin/aysfs' % self.root

        if not j.sal.fs.exists(binary):
            print('[+] downloading aysfs binary')
            storx = j.clients.storx.get('https://stor.jumpscale.org/storx')
            storx.getStaticFile('aysfs', binary)
            j.sal.fs.chmod(binary, 0o755)

    def start(self):
        # ensure that all required path and binaries exists
        self._install()

        # parsing paths (replaces names)
        self._parse(self.mounts)
        self._parse(self.backends)

        print('[+] preparing mountpoints')
        for mount in self.mounts:
            # force umount (cannot stat folder if Transport endpoint is not connected)
            self.unmount(mount['path'])

            if not j.sal.fs.exists(mount['path']):
                j.sal.fs.createDir(mount['path'])

        print('[+] checking backends')
        for backend in self.backends:
            if not j.sal.fs.exists(backend['path']):
                j.sal.fs.createDir(backend['path'])

        print('[+] writing config file')
        config = '%s/etc/%s.toml' % (self.root, self.name)
        j.sal.fs.writeFile(config, self.generate())

        print('[+] starting aysfs')

        cmdline = '%s/bin/aysfs -config %s' % (self.root, config)
        self.tmux.executeInScreen('aysfs', config, cmdline)

        return True

    def stop(self):
        config = '%s/etc/%s.toml' % (self.root, self.name)
        self.tmux.killWindow('aysfs', config)

    def isRunning(self):
        config = '%s/etc/%s.toml' % (self.root, self.name)
        return self.tmux.windowExists('aysfs', config)
