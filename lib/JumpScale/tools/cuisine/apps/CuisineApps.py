
from JumpScale import j

# decorator
from ActionDecorator import ActionDecorator

# module imports
from apps.CuisineSkyDns import SkyDns
from apps.CuisineCaddy import Caddy
from apps.CuisineAydoStor import AydoStor
from apps.CuisineSyncthing import Syncthing
from apps.CuisineRedis import Redis
from apps.CuisineMongodb import Mongodb
from apps.CuisineFs import Fs
from apps.CuisineEtcd import Etcd
from apps.CuisineController import Controller
from apps.CuisineCoreOs import Core
from apps.CuisineGrafana import Grafana
from apps.CuisineInfluxdb import Influxdb
from apps.CuisineVulcand import Vulcand
from apps.CuisineWeave import Weave
from apps.CuisinePortal import CuisinePortal
from apps.CuisineCockpit import Cockpit
from apps.CuisineDeployerBot import DeployerBot
from apps.CuisineHadoop import Hadoop
from apps.CuisineArakoon import Arakoon
from apps.CuisineVolumeDriver import VolumeDriver
from apps.CuisineAlba import Alba
from apps.CuisineLedis import Ledis

import time

"""
please ensure that the start and build methods are separate and
the build doesnt place anyfile outside opt as it will be used in aysfs mounted system
"""


class actionrun(ActionDecorator):

    def __init__(self, *args, **kwargs):
        ActionDecorator.__init__(self, *args, **kwargs)
        self.selfobjCode = "cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.apps"

base = j.tools.cuisine.getBaseClass()


class CuisineApps(base):

    def __init__(self, executor, cuisine):
        self.executor = executor
        self.cuisine = cuisine

        # imported properties
        self._skydns = None
        self._caddy = None
        self._stor = None
        self._syncthing = None
        self._redis = None
        self._mongodb = None
        self._fs = None
        self._etcd = None
        self._controller = None
        self._grafana = None
        self._influxdb = None
        self._core = None
        self._vulcand = None
        self._weave = None
        self._portal = None
        self._cockpit = None
        self._deployerbot = None
        self._arakoon = None
        self._volumedriver = None
        self._alba = None
        self._hadoop = None
        self._ledis = None

    @property
    def weave(self):
        if self._weave is None:
            if not self.cuisine.core.isDocker and not self.cuisine.core.isLxc:
                self._weave = Weave(self.executor, self.cuisine)
            else:
                raise AttributeError('Weave does not support LXC or Docker containers')
        return self._weave

    @property
    def skydns(self):
        if self._skydns is None:
            self._skydns = SkyDns(self.executor, self.cuisine)
        return self._skydns

    @property
    def caddy(self):
        if self._caddy is None:
            self._caddy = Caddy(self.executor, self.cuisine)
        return self._caddy

    @property
    def stor(self):
        if self._stor is None:
            self._stor = AydoStor(self.executor, self.cuisine)
        return self._stor

    @property
    def syncthing(self):
        if self._syncthing is None:
            self._syncthing = Syncthing(self.executor, self.cuisine)
        return self._syncthing

    @property
    def redis(self):
        if self._redis is None:
            self._redis = Redis(self.executor, self.cuisine)
        return self._redis

    @property
    def mongodb(self):
        if self._mongodb is None:
            self._mongodb = Mongodb(self.executor, self.cuisine)
        return self._mongodb

    @property
    def fs(self):
        if self._fs is None:
            self._fs = Fs(self.executor, self.cuisine)
        return self._fs

    @property
    def etcd(self):
        if self._etcd is None:
            self._etcd = Etcd(self.executor, self.cuisine)
        return self._etcd

    @property
    def controller(self):
        if self._controller is None:
            self._controller = Controller(self.executor, self.cuisine)
        return self._controller

    @property
    def core(self):
        if self._core is None:
            self._core = Core(self.executor, self.cuisine)
        return self._core

    @property
    def grafana(self):
        if self._grafana is None:
            self._grafana = Grafana(self.executor, self.cuisine)
        return self._grafana

    @property
    def influxdb(self):
        if self._influxdb is None:
            self._influxdb = Influxdb(self.executor, self.cuisine)
        return self._influxdb

    @property
    def vulcand(self):
        if self._vulcand is None:
            self._vulcand = Vulcand(self.executor, self.cuisine)
        return self._vulcand

    @property
    def portal(self):
        if self._portal is None:
            self._portal = CuisinePortal(self.executor, self.cuisine)
        return self._portal

    @property
    def cockpit(self):
        if self._cockpit is None:
            self._cockpit = Cockpit(self.executor, self.cuisine)
        return self._cockpit

    @property
    def deployerbot(self):
        if self._deployerbot is None:
            self._deployerbot = DeployerBot(self.executor, self.cuisine)
        return self._deployerbot

    @property
    def arakoon(self):
        if self._arakoon is None:
            self._arakoon = Arakoon(self.executor, self.cuisine)
        return self._arakoon

    @property
    def volumedriver(self):
        if self._volumedriver is None:
            self._volumedriver = VolumeDriver(self.executor, self.cuisine)
        return self._volumedriver

    @property
    def alba(self):
        if self._alba is None:
            self._alba = Alba(self.executor, self.cuisine)
        return self._alba

    @property
    def hadoop(self):
        if self._hadoop is None:
            self._hadoop = Hadoop(self.executor, self.cuisine)
        return self._hadoop

    @property
    def ledis(self):
        if self._ledis is None:
            self._ledis = Ledis(self.executor, self.cuisine)
        return self._ledis

    @actionrun(action=True)
    def installdeps(self):
        pass
        # NO NEED TO DO ITS UPTO USER OF CUISINE TO MAKE SURE REQUIREMENTS ARE MET
        # self.cuisine.installer.base()
        # self.cuisine.golang.install()
        # self.cuisine.pip.upgrade('pip')
