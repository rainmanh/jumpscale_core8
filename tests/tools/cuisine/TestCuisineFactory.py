"""
Test module for CuisineFactory
"""

import unittest
from unittest import mock


class TestCuisineFactory(unittest.TestCase):
    def setUp(self):
        from JumpScale import j
        self.factory = j.tools.cuisine

    def tearDown(self):
        pass


    def test_create_factory(self):
        """
        Test creating a factory instance
        """
        with mock.patch("JumpScale.j") as j_mock:
            from JumpScale import j
            import JumpScale.tools.cuisine.CuisineFactory
            JumpScale.tools.cuisine.CuisineFactory.j = j
            from JumpScale.tools.cuisine.CuisineFactory import JSCuisineFactory
            factory = JSCuisineFactory()


    def test_get_local(self):
        """
        Test getting a local cuisine instance
        """
        with mock.patch("JumpScale.j") as j_mock:
            with mock.patch("Cuisine2.JSCuisine") as jscuisine_mock:
                from JumpScale import j
                import JumpScale.tools.cuisine.CuisineFactory
                JumpScale.tools.cuisine.CuisineFactory.j = j
                from JumpScale.tools.cuisine.CuisineFactory import JSCuisineFactory
                factory = JSCuisineFactory()
                old_local = factory.local
                new_local = factory.local
                self.assertEqual(old_local, new_local)
                old_local = factory.local
                factory._local = None
                new_local = factory.local
                self.assertNotEqual(old_local, new_local)

    @mock.patch('JumpScale.j.clients.ssh')
    @mock.patch('JumpScale.j.tools.console')
    @mock.patch('JumpScale.j.tools.executor')
    def test_get_push_key_if_ssh_client_returned(self, mock_executor, mock_console, mock_ssh):
        """
        Test getting ssh executor
        """
        # check the path where the password is not set
        mock_ssh.get.return_value = True
        self.factory.getPushKey()
        self.assertTrue(mock_executor.getSSHBased.called)
        self.assertFalse(mock_console.askPassword.called)

    @mock.patch('JumpScale.j.clients.ssh')
    @mock.patch('JumpScale.j.sal.process')
    @mock.patch('JumpScale.j.tools.console')
    def test_get_push_key_if_ssh_client_error(self, mock_console, mock_process, mock_ssh):
        """
        Test getting ssh executor
        """
        mock_ssh.get.return_value = False
        ssh_add_l_output = (0, '2048 SHA256:C7QPiMG99B+2XP/WV6Uwqdi/VIGf7Mglq74FPVHlvw0 abdelrahman@abdelrahman-work (RSA)')
        mock_process.execute.return_value = ssh_add_l_output
        self.factory.getPushKey()
        self.assertTrue(mock_console.askPassword.called)
        self.assertTrue(mock_console.askChoice.called)
