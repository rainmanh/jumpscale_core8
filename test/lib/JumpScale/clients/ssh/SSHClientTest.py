"""
Unit tests module for lib.Jumpscale.clients.ssh.SSHClient module
"""

import unittest2 as unittest
import mock


class SSHClientTest(unittest.TestCase):
    """
    Test SSHClient class
    """

    def test_sshclientfactory_get(self):
        """
        Tests getting new client using the client factory
        """
        with mock.patch('Jumpscale') as js_mock:
            from lib.Jumpscale.clients.ssh import SSHClient
            with mock.patch('j.data.hash.md5_string') as md5_string_mock:
                md5_string_mock.return_value = 'pass'
                SSHClient.SSHClient = mock.Mock()
                sshclient_factory = SSHClient.SSHClientFactory()
                sshclinet = sshclient_factory.get(addr="localhost")
