"""
Unit tests module for lib.Jumpscale.clients.ssh.SSHClient module
"""

import unittest2 as unittest
import mock
from test.surrogate import surrogate
from lib.JumpScale import j

class SSHClientTest(unittest.TestCase):
    """
    Test SSHClient class
    """
    # @surrogate('j.data.hash.md5_string')
    def test_sshclientfactory_get(self):
        """
        Tests getting new client using the client factory
        """
        j.data.hash.md5_string('hello')
        from lib.JumpScale.clients.ssh import SSHClient

        with mock.patch('j.data.hash.md5_string') as md5_string_mock:
            md5_string_mock.return_value = 'pass'
            j.data.hash.md5_string('hello')

            raise RuntimeError(md5_string_mock.called)
            expected_key = "%s_%s_%s_%s" % ('localhost', 22, 'root', 'pass')
            SSHClient.SSHClient = mock.Mock()
            sshclient_factory = SSHClient.SSHClientFactory()
            sshclinet = sshclient_factory.get(addr="localhost")

            raise RuntimeError(sshclient_factory.cache)
            # assert
            self.assertTrue(expected_key in sshclient_factory.cache)

    # @surrogate('j.data.hash.md5_string')
    # def test_sshclientfactory_get_raises_exception(self):
    #     """
    #     Tests getting new client using the client factory fails when testing
    #     the connection fails
    #     """
    #     from lib.JumpScale.clients.ssh import SSHClient
    #     with mock.patch('j.data.hash.md5_string') as md5_string_mock:
    #         md5_string_mock.return_value = 'pass'
    #         expected_key = "%s_%s_%s_%s" % ('localhost', 22, 'root', 'pass')
    #         SSHClient.SSHClient = mock.Mock()
    #         SSHClient.SSHClient.connectTest.return_value = False
    #         sshclient_factory = SSHClient.SSHClientFactory()
    #         sshclinet = sshclient_factory.get(addr="localhost", testConnection=False)
    #
    #         # assert
    #         self.assertTrue(expected_key in sshclient_factory.cache)
