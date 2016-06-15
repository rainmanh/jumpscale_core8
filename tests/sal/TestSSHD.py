import unittest

from JumpScale import j

class TestSSHD(unittest.TestCase):

    def setUp(self):
        self.sshd = j.sal.sshd
        self.key1 = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCUlY0UEUNExAQF/sIw2L2AJEmHj0eTCnSCwg7gYOQDNhrrzD0+HJulD1UTz+zZqiC2nIPWMfWBoEs3i4jDj79fyiGx4pgQJXFwioIqTONlEyvPIY0eCm3eeSaWrK9G0STdlCrrofZzuAL5/SCKiqTEizZe1MqhJT/xs2xpD+hHFIyMIuBl9OOLX2XvFQ6mBB1bq4U1jpemuHk7L/M0m73Na4M2CQWVDUl/CRhNyhI+WlB2i9dwI3RwrtUp98MCAF//cx3xVC4NfHONQmN8j7z/WpsfJIadqOxfnOp5y4kj1EqbtmeKZbYvR2ZtcAibcnWs0/4kNDn723NheG/secHT root@myjs8xenial'
        self.key2 = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCUlY0UEUNExAQF/sIw2L2AJEmHj0eTCnSCwg7gYOQDNhrrzD0+HJulD1UTz+zZqiC2nIPWMfWBoEs3i4jDj79fyiGx4pgQJXFwioIqTONlEyvPIY0eCm3eeSaWrK9G0STdlCrrofZzuAL5/SCKiqTEizZe1MqhJT/xs2xpD+hHFIyMIuBl9OOLX2XvFQ6mBB1bq4U1jpemuHk7L/M0m73Na4M2CQWVDUl/CRhNyhI+WlB2i9dwI3RwrtUp98MCAF//cx3xVC4NfHONQmN8j7z/WpsfJIadqOxfnOp5y4kj1EqbtmeKZbYvR2ZtcAibcnWs0/4kNDn723NheG/secHT root@myjs8xenial2'
        self.sshroot= j.tools.path.get("/tmp/sshroot")

        self.authkeysfile = j.tools.path.get("/tmp/sshroot/authkeys")

        j.sal.fs.createDir(self.sshroot)
        j.sal.fs.touch(self.authkeysfile)

        self.sshd.commit()
        self.sshd.SSH_ROOT = self.sshroot
        self.sshd.SSH_AUTHORIZED_KEYS = self.authkeysfile

    def tearDown(self):
        j.sal.fs.removeDirTree("/tmp/sshroot/authkeys")

    def test_list_keys_emptyfile(self):
        self.assertEqual(len(self.sshd.keys), 0)

    def test_list_keys(self):
        self.sshd.addKey(self.key1)
        self.sshd.addKey(self.key2)
        self.sshd.commit()

        self.assertEqual(len(self.sshd.keys), 2)
        self.assertIn(self.key1, self.sshd.keys)
        self.assertIn(self.key2, self.sshd.keys)

    def test_add_key(self):
        self.sshd.addKey(self.key1)
        self.sshd.addKey(self.key2)
        self.sshd.commit()

        self.assertEqual(len(self.sshd.keys), 2)

    def test_key_exists_after_add(self):
        self.sshd.addKey(self.key1)
        self.sshd.addKey(self.key2)
        self.sshd.commit()

        self.assertEqual(len(self.sshd.keys), 2)
        self.assertIn(self.key1, self.sshd.keys)

    def test_key_doesntexists_after_delete(self):
        self.sshd.addKey(self.key1)
        self.sshd.addKey(self.key2)
        self.sshd.commit()

        self.assertEqual(len(self.sshd.keys), 2)
        self.assertIn(self.key1, self.sshd.keys)

        self.sshd.deleteKey(self.key1)
        self.sshd.commit()
        
        self.assertNotIn(self.key1, self.sshd.keys)

    def test_erase(self):
        self.sshd.addKey(self.key1)
        self.sshd.addKey(self.key2)
        self.sshd.commit()

        self.assertEqual(len(self.sshd.keys), 2)

        self.sshd.erase()
        self.sshd.commit()

        self.assertEqual(len(self.sshd.keys), 0)


    def test_delete_key(self):

        self.sshd.addKey(self.key1)
        self.sshd.addKey(self.key2)
        self.sshd.commit()

        self.assertEqual(len(self.sshd.keys), 2)

        self.sshd.deleteKey(self.key2)
        self.sshd.commit()

        self.assertEqual(len(self.sshd.keys), 1)

