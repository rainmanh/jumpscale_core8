import unittest
from JumpScale import j

descr = """
AtYourService Tests
"""

organization = "jumpscale"
author = "christophe dCPM"
license = "bsd"
version = "1.0"
category = "app.ays.unittest"
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
        self.tmp_dir = j.sal.fs.getTmpDirPath()
        self.services_dir = j.sal.fs.joinPaths(self.tmp_dir, 'services')
        self.templates_dir = j.sal.fs.joinPaths(self.tmp_dir, 'servicetemplates')
        self.domain = j.sal.fs.getBaseName(self.tmp_dir)
        # create ays directories
        j.sal.fs.createDir(self.tmp_dir)
        j.sal.fs.createDir(self.services_dir)
        j.sal.fs.createDir(self.templates_dir)

        # copy templates fixtures in place
        parent = j.sal.fs.getParent(__file__)
        src = j.sal.fs.joinPaths(parent, 'fixtures')
        j.sal.fs.copyDirTree(src, self.templates_dir)
        j.sal.fs.changeDir(self.tmp_dir)

    @classmethod
    def tearDownClass(self):
        if j.sal.fs.exists(path=self.tmp_dir):
            j.sal.fs.removeDirTree(self.tmp_dir)
            j.sal.fs.changeDir("/opt")  # need to move in an existing folder otherwise unittest gives errors

        # reset ays status
        j.atyourservice.services = []
        j.atyourservice.templates = []
        j.atyourservice._init = False
        j.atyourservice._domains = []


class AYSNew(AYSTestBase):

    def setUp(self):
        """
        executed before each test method.
        """
        j.sal.fs.changeDir(self.tmp_dir)

    def tearDown(self):
        """
        executed after each test method.
        """

    def test_new(self):
        """
        test create new services
        """
        s = j.atyourservice.new(name='template1')
        self.assertEqual(s.path, j.sal.fs.joinPaths(self.services_dir, 'template1__main'))
        self.assertEqual(s.domain, self.domain)
        self.assertEqual(s.name, 'template1')
        self.assertEqual(s.instance, 'main')
        self.assertEqual(s.getKey(), '%s|%s!%s' % (s.domain, s.name, s.instance))
        self.assertEqual(s.instance, 'main')

    def test_args(self):
        """
        args can be prefix with 'instance.' or not and should work
        """
        args = {
            'instance.arg.1': 'foo',
            'arg.2': 'bar',
        }
        s = j.atyourservice.new(name='templateargs', args=args)
        self.assertEqual(s.hrd.getStr('instance.arg.1'), 'foo')
        self.assertEqual(s.hrd.getStr('instance.arg.2'), 'bar')

    def test_consume(self):
        s2 = j.atyourservice.new(name='template2')
        s2.init()

        consume = s2.getKey()
        s3 = j.atyourservice.new(name='template3', consume=consume)
        s3.init()
        self.assertEqual(len(s3.producers), 1)
        self.assertTrue('template2' in s3.producers)


class AYSParent(AYSTestBase):

    def setUp(self):
        """
        executed before each test method.
        """
        j.sal.fs.changeDir(self.tmp_dir)

    def tearDown(self):
        """
        executed after each test method.
        """
    def test_parent(self):
        # test if two service can have same instance name if under different parents
        parent1 = j.atyourservice.new(name='template1', instance='parent1')
        parent2 = j.atyourservice.new(name='template1', instance='parent2')

        child1 = j.atyourservice.new(name='template2', instance='main', parent=parent1)
        child2 = j.atyourservice.new(name='template2', instance='main', parent=parent2)

        self.assertEqual(len(j.atyourservice.findServices(name='template2')), 2)
        self.assertNotEqual(child1.getKey(), child2.getKey())

        s = j.atyourservice.getSetvice(name='template2', instance='main', parent=parent1)
        self.assertEqual(s.parent.getKey(), parent1.getKey())
        self.assertTrue(s.path.find(parent.path) != -1)


class AYSFindService(AYSTestBase):

    def setUp(self):
        """
        executed before each test method.
        """
        s1a = j.atyourservice.new(name='template1', instance='main')
        self.parent = s1a
        s1b = j.atyourservice.new(name='template1', instance='foo')
        s2c = j.atyourservice.new(name='template1', instance='bar')

        s2a = j.atyourservice.new(name='template2', instance='main')

        s3a = j.atyourservice.new(name='template3', instance='main')

        s4 = j.atyourservice.new(name='template3', instance='main', parent=s1a)

    def tearDown(self):
        """
        executed after each test method.
        """
        for path in j.sal.fs.listDirsInDir(self.services_dir):
            j.sal.fs.removeDirTree(path)

    def test_findService(self):
        """
        test findServices
        """
        self.assertEqual(len(j.atyourservice.findServices()), 6)
        self.assertEqual(len(j.atyourservice.findServices(name='template1')), 3)
        self.assertEqual(len(j.atyourservice.findServices(name='noexists')), 0)
        self.assertEqual(len(j.atyourservice.findServices(instance='main')), 4)
        self.assertEqual(len(j.atyourservice.findServices(instance='foo')), 1)
        self.assertEqual(len(j.atyourservice.findServices(name='template1', instance='main')), 1)
        self.assertEqual(len(j.atyourservice.findServices(name='template3', instance='noexists')), 0)
        self.assertEqual(len(j.atyourservice.findServices(parent=self.parent)), 1)
        self.assertEqual(len(j.atyourservice.findServices(name='template2', parent=self.parent)), 0)
        self.assertEqual(len(j.atyourservice.findServices(domain='jumpscale')), 0)

class AYSKey(AYSTestBase):

    def setUp(self):
        """
        executed before each test method.
        """

    def tearDown(self):
        """
        executed after each test method.
        """
        for path in j.sal.fs.listDirsInDir(self.services_dir):
            j.sal.fs.removeDirTree(path)

    def test_parseKey(self):
        """
        $domain!$name:$instance@role ($version)
        should return (domain,name,version,instance,role)
        """
        test_table = [
            {
                'input': 'jumpscale!-redis:main@kv (0.1)',
                'domain': 'jumpscale',
                'name': 'redis',
                'instance': 'main',
                'role': 'kv',
                'version': '0.1',
            },
        ]
        for test in test_table:
            domain, name, version, instance, role = j.atyourservice.parseKey(test['input'])
            self.assertEqual(domain, test['domain'])
            self.assertEqual(name, test['name'])
            self.assertEqual(version, test['version'])
            self.assertEqual(instance, test['instance'])
            self.assertEqual(role, test['role'])