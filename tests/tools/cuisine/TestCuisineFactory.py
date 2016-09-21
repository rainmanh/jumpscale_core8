"""
Test module for CuisineFactory
"""

import unittest
from unittest import mock
from JumpScale import j


class TestCuisineFactory(unittest.TestCase):
    def setUp(self):
        self.factory = j.tools.cuisine
        self.ssh_add_l_output = (0, '2048 SHA256:C7QPiMG99B+2XP/WV6Uwqdi/VIGf7Mglq74FPVHlvw0 abdelrahman@abdelrahman-work (RSA)')


    def tearDown(self):
        pass

    def test_get_local(self):
        """
        Test getting a local cuisine instance
        """
        old_local = self.factory.local
        new_local = self.factory.local
        self.assertEqual(old_local, new_local)
        old_local = self.factory.local
        self.factory._local = None
        new_local = self.factory.local
        self.assertNotEqual(old_local, new_local)

    @mock.patch('JumpScale.j.tools.console')
    @mock.patch('JumpScale.j.sal.fs')
    @mock.patch('JumpScale.j.do')
    @mock.patch('JumpScale.j.sal.process')
    def test_generate_pubkey_loads_ssh_agent_if_none_found(self, mock_process, mock_do, mock_fs, mock_console):
        """
        Happy Path. If checkSSHAgentAvailable returns False
        """
        # Mocking
        mock_do.checkSSHAgentAvailable.return_value = False
        mock_process.execute.return_value = self.ssh_add_l_output
        mock_console.askChoice.return_value = 'abdelrahman@abdelrahman-work'
        mock_fs.fileGetContents.return_value = 'random key'
        # Calling the method
        self.factory._generate_pubkey()
        # Assertions
        mock_do.checkSSHAgentAvailable.assert_called_once_with()
        mock_do._loadSSHAgent.assert_called_once_with()
        mock_process.execute.assert_called_once_with('ssh-add -l')
        mock_console.askChoice.assert_called_once_with(['abdelrahman@abdelrahman-work'], 'please select key')
        mock_fs.fileGetContents.assert_called_once_with('abdelrahman@abdelrahman-work.pub')

    @mock.patch('JumpScale.j.tools.console')
    @mock.patch('JumpScale.j.sal.fs')
    @mock.patch('JumpScale.j.do')
    @mock.patch('JumpScale.j.sal.process')
    def test_generate_pubkey_loads_ssh_agent_is_found(self, mock_process, mock_do, mock_fs, mock_console):
        """
        Happy Path. If checkSSHAgentAvailable returns True
        """
        # Mocking
        mock_do.checkSSHAgentAvailable.return_value = True
        mock_process.execute.return_value = self.ssh_add_l_output
        mock_console.askChoice.return_value = 'abdelrahman@abdelrahman-work'
        mock_fs.fileGetContents.return_value = 'random key'
        # Calling the method
        self.factory._generate_pubkey()
        # Assertions
        mock_do.checkSSHAgentAvailable.assert_called_once_with()
        mock_do._loadSSHAgent.assert_not_called()
        mock_process.execute.assert_called_once_with('ssh-add -l')
        mock_console.askChoice.assert_called_once_with(['abdelrahman@abdelrahman-work'], 'please select key')
        mock_fs.fileGetContents.assert_called_once_with('abdelrahman@abdelrahman-work.pub')

    @unittest.skip("No longer represent the method")
    @mock.patch('JumpScale.j.clients.ssh')
    @mock.patch('JumpScale.j.tools.console')
    @mock.patch('JumpScale.j.tools.executor')
    def test_get_push_key_if_ssh_client_returned(self, mock_executor, mock_console, mock_ssh):
        """
        Test getting ssh executor
        """
        # check the path where the password is not set
        mock_ssh.get.return_value = True
        self.factory.authorizeKey()
        self.assertTrue(mock_executor.getSSHBased.called)
        self.assertFalse(mock_console.askPassword.called)

    @unittest.skip("No longer represent the method")
    @mock.patch('JumpScale.j.clients.ssh')
    @mock.patch('JumpScale.j.sal.process')
    @mock.patch('JumpScale.j.tools.console')
    def test_get_push_key_if_ssh_client_error(self, mock_console, mock_process, mock_ssh):
        """
        Test getting ssh executor
        """
        mock_ssh.get.return_value = False
        mock_process.execute.return_value = self.ssh_add_l_output
        self.factory.getPushKey()
        self.assertTrue(mock_console.askPassword.called)
        self.assertTrue(mock_console.askChoice.called)
