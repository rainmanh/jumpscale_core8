"""
Test JSCuisine  (core)
"""
import unittest
from unittest import mock

from JumpScale import j
from JumpScale.tools.cuisine.JSCuisine import JSCuisine
import JumpScale
from JumpScale.tools.cuisine.ProcessManagerFactory import ProcessManagerFactory

class TestJSCuisine(unittest.TestCase):
    def setUp(self):
        self._local_executor = j.tools.executor.getLocal()
        self.JSCuisine = JSCuisine(self._local_executor)

    def tearDown(self):
        pass

    def test_create_cuisine2(self):
        """
        Test creating an instance
        """
        self.assertIsNotNone(self.JSCuisine.core)
        self.assertIsNotNone(self.JSCuisine.tools.sshreflector)
        self.assertIsNotNone(self.JSCuisine.solutions.proxyclassic)
        self.assertIsNotNone(self.JSCuisine.tools.bootmediainstaller)
        self.assertIsNotNone(self.JSCuisine.solutions.vrouter)
        self.assertIsNotNone(self.JSCuisine.tmux)
        self.assertIsNotNone(self.JSCuisine.pnode)
        self.assertIsNotNone(self.JSCuisine.tools.stor)

    def test_create_cuisine2_platformtype(self):
        """
        Test accessing platformtype property
        """
        self.assertIsNotNone(self.JSCuisine.platformtype)

    def test_create_cuisine2_id(self):
        """
        Test accessing id property
        """
        self.assertIsNotNone(self.JSCuisine.id)

    def test_create_cuisine2_btrfs(self):
        """
        Test accessing btrfs property
        """
        self.assertIsNotNone(self.JSCuisine.btrfs)

    def test_create_cuisine2_package(self):
        """
        Test accessing package property
        """
        self.assertIsNotNone(self.JSCuisine.package)

    def test_create_cuisine2_process(self):
        """
        Test accessing process property
        """
        self.assertIsNotNone(self.JSCuisine.process)

    def test_create_cuisine2_pip_is_not_None(self):
        """
        Test accessing pip property
        """
        self.assertIsNotNone(self.JSCuisine.development.pip)


    def test_create_cuisine2_fw(self):
        """
        Test accessing fw property
        """
        self.assertIsNotNone(self.JSCuisine.systemservices.ufw)

    def test_create_cuisine2_golang(self):
        """
        Test accessing golang property
        """
        self.assertIsNotNone(self.JSCuisine.development.golang)

    def test_create_cuisine2_geodns(self):
        """
        Test accessing geodns property
        """
        self.assertIsNotNone(self.JSCuisine.apps.geodns)

    def test_create_cuisine2_apps(self):
        """
        Test accessing apps property
        """
        self.assertIsNotNone(self.JSCuisine.apps)

    @unittest.skip("Builder is removed while writing this")
    def test_create_cuisine2_builder(self):
        """
        Test accessing builder property
        """
        self.assertIsNotNone(self.JSCuisine.builder)

    def test_create_cuisine2_ns(self):
        """
        Test accessing ns property
        """
        self.assertIsNotNone(self.JSCuisine.ns)

    def test_create_cuisine2_docker(self):
        """
        Test accessing docker property
        """
        self.assertIsNotNone(self.JSCuisine.systemservices.docker)

    def test_create_cuisine2_ssh(self):
        """
        Test accessing ssh property
        """
        self.assertIsNotNone(self.JSCuisine.ssh)

    @unittest.skip("couldn't find avahi")
    def test_create_cuisine2_avahi(self):
        """
        Test accessing avahi property
        """
        self.assertIsNotNone(self.JSCuisine.avahi)

    def test_create_cuisine2_bash(self):
        """
        Test accessing bash property
        """
        self.assertIsNotNone(self.JSCuisine.bash)

    def test_create_cuisine2_net(self):
        """
        Test accessing net property
        """
        self.assertIsNotNone(self.JSCuisine.net)

    def test_create_cuisine2_user_is_not_None(self):
        """
        Test accessing user property
        """
        self.assertIsNotNone(self.JSCuisine.user)

    def test_create_cuisine2_group(self):
        """
        Test accessing group property
        """
        self.assertIsNotNone(self.JSCuisine.group)


    def test_create_cuisine2_git(self):
        """
        Test accessing git property
        """
        self.assertIsNotNone(self.JSCuisine.development.git)


    @mock.patch('JumpScale.tools.cuisine.ProcessManagerFactory.ProcessManagerFactory')
    def test_create_cuisine2_processmanager(self, processmanager_mock):
        """
        Test accessing processmanager property
        """
        processmanager_mock.get.return_value = ProcessManagerFactory(self.JSCuisine)
        self.assertIsNotNone(self.JSCuisine.processmanager)
