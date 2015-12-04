import unittest
from JumpScale import j

descr = """
AtYourService Tests
"""

organization = "jumpscale"
author = "christophe dCPM"
license = "bsd"
version = "1.0"
category = "app.ays.integration"
enable = True
priority = 1
send2osis = False


class AYSTestBase(unittest.TestCase):
    """Base class for AYS Test"""

    @classmethod
    def setUpClass(self):
        """
        creates a directory where we can run the test in isolation
        """
        self.tmp_dir = j.system.fs.getTmpDirPath()
        self.services_dir = j.system.fs.joinPaths(self.tmp_dir, 'services')
        self.templates_dir = j.system.fs.joinPaths(self.tmp_dir, 'servicetemplates')
        self.domain = j.system.fs.getBaseName(self.tmp_dir)
        # create ays directories
        j.system.fs.createDir(self.tmp_dir)
        j.system.fs.createDir(self.services_dir)
        j.system.fs.createDir(self.templates_dir)

        # copy templates fixtures in place
        parent = j.system.fs.getParent(__file__)
        src = j.system.fs.joinPaths(parent, 'fixtures')
        j.system.fs.copyDirTree(src, self.templates_dir)
        j.system.fs.changeDir(self.tmp_dir)

    @classmethod
    def tearDownClass(self):
        if j.system.fs.exists(path=self.tmp_dir):
            j.system.fs.removeDirTree(self.tmp_dir)
            j.system.fs.changeDir("/opt")  # need to move in an existing folder otherwise unittest gives errors

        # reset ays status
        j.atyourservice.services = []
        j.atyourservice.templates = []
        j.atyourservice._init = False
        j.atyourservice._domains = []


class AYSInit(AYSTestBase):

    def setUp(self):
        """
        executed before each test method.
        """
        j.system.fs.changeDir(self.tmp_dir)

    def tearDown(self):
        """
        executed after each test method.
        """

    def test_init(self):
        """
        """
    pass
