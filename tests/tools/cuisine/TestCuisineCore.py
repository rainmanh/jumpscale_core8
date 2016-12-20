"""
Test CuisineCore module
"""
import unittest
from unittest.mock import patch, PropertyMock
import copy

from JumpScale import j


@patch('JumpScale.core.redis.Redis.hget')
@patch('JumpScale.core.redis.Redis.hset')
class TestCuisineCore(unittest.TestCase):

    def setUp(self):
        self.dump_env = {
            'HOME': '/root',
            'HOSTNAME': 'js8-core',
            'JSBASE': '/js/path',
        }
        self.core = j.tools.cuisine.local.core
        self.dir_paths = {'JSAPPSDIR': '/js/path/apps',
                          'base': '/js/path',
                          'BINDIR': '/js/path/bin',
                          'JSCFGDIR': '/optvar//cfg',
                          'CODEDIR': '/opt/code/',
                          'GODIR': '/optvar/go/',
                          'HOMEDIR': '/root',
                          'HRDDIR': '/optvar//hrd',
                          'JSLIBDIR': '/js/path/lib/JumpScale/',
                          'LIBDIR': '/js/path/lib/',
                          'LOGDIR': '/optvar//log',
                          'optDir': '/opt/',
                          'PIDDIR': '/optvar//pid',
                          'TMPDIR': '/optvar//tmp',
                          'TEMPLATEDIR': '/js/path/templates',
                          'VARDIR': '/optvar/'
                          }

    def tearDown(self):
        pass

    def test_isJS8Sandbox_property(self, cache_set_mock, cache_get_mock):
        """
        Test accessing the isJS8Sandbox property
        """
        cache_get_mock.return_value = None
        self.assertIsNotNone(self.core.isJS8Sandbox)

    @patch('JumpScale.j.tools.cuisine.local.core.getenv')
    def test_dir_paths_property_if_JSBASE_and_linux(self, getenv_mock, cache_set_mock, cache_get_mock):
        """
        Happy Path: Test accessing the dir_paths property if JSBASE in env
        """
        cache_get_mock.return_value = None
        getenv_mock.return_value = self.dump_env
        result = self.core.dir_paths
        self.assertEqual(result, self.dir_paths)

    @patch('JumpScale.j.tools.cuisine.local.core.getenv')
    def test_dir_paths_property_if_linux(self, getenv_mock, cache_set_mock, cache_get_mock):
        """
        Happy Path: Test accessing the dir_paths property if JSBASE not found in env
        """
        cache_get_mock.return_value = None

        # remove JSBASE from dump_env
        dump_env = copy.deepcopy(self.dump_env)
        del dump_env['JSBASE']
        getenv_mock.return_value = dump_env

        expected_result = {
            'JSAPPSDIR': '/opt/jumpscale8//apps',
            'base': '/opt/jumpscale8/',
            'BINDIR': '/opt/jumpscale8//bin',
            'JSCFGDIR': '/optvar//cfg',
            'CODEDIR': '/opt/code/',
            'GODIR': '/optvar/go/',
            'HOMEDIR': '/root',
            'HRDDIR': '/optvar//hrd',
            'JSLIBDIR': '/opt/jumpscale8//lib/JumpScale/',
            'LIBDIR': '/opt/jumpscale8//lib/',
            'LOGDIR': '/optvar//log',
            'optDir': '/opt/',
            'PIDDIR': '/optvar//pid',
            'TMPDIR': '/optvar//tmp',
            'TEMPLATEDIR': '/opt/jumpscale8//templates',
            'VARDIR': '/optvar/'
        }
        result = self.core.dir_paths
        self.assertEqual(result, expected_result)

    @patch('JumpScale.tools.cuisine.CuisineCore.CuisineCore.isMac', new_callable=PropertyMock)
    @patch('JumpScale.j.tools.cuisine.local.core.getenv')
    def test_dir_paths_property_if_not_linux(self, getenv_mock, mac_mock, cache_set_mock, cache_get_mock):
        """
        Happy Path: Test accessing the dir_paths property if JSBASE not found in env and not linux
        """
        cache_get_mock.return_value = None
        mac_mock.return_value = True

        # remove JSBASE from dump_env
        dump_env = copy.deepcopy(self.dump_env)
        del dump_env['JSBASE']
        getenv_mock.return_value = dump_env

        expected_result = {
            'JSAPPSDIR': '/root/opt/jumpscale8//apps',
            'base': '/root/opt/jumpscale8/',
            'BINDIR': '/root/opt/jumpscale8//bin',
            'JSCFGDIR': '/root/optvar//cfg',
            'CODEDIR': '/root/opt/code/',
            'GODIR': '/root/optvar/go/',
            'HOMEDIR': '/root',
            'HRDDIR': '/root/optvar//hrd',
            'JSLIBDIR': '/root/opt/jumpscale8//lib/JumpScale/',
            'LIBDIR': '/root/opt/jumpscale8//lib/',
            'LOGDIR': '/root/optvar//log',
            'optDir': '/root/opt/',
            'PIDDIR': '/root/optvar//pid',
            'TMPDIR': '/root/optvar//tmp',
            'TEMPLATEDIR': '/root/opt/jumpscale8//templates',
            'VARDIR': '/root/optvar/'
        }
        result = self.core.dir_paths
        self.assertEqual(result, expected_result)
        self.assertEqual(mac_mock.call_count, 2)

    @patch('JumpScale.tools.cuisine.CuisineCore.CuisineCore.isMac', new_callable=PropertyMock)
    @patch('JumpScale.j.tools.cuisine.local.core.getenv')
    def test_dir_paths_property_if_JSBASE_and_not_linux(self, getenv_mock, mac_mock, cache_set_mock, cache_get_mock):
        """
        Happy Path: Test accessing the dir_paths property if JSBASE in env and not linux
        """
        cache_get_mock.return_value = None
        mac_mock.return_value = True
        getenv_mock.return_value = self.dump_env

        expected_result = {
            'JSAPPSDIR': '/js/path/apps',
            'base': '/js/path',
            'BINDIR': '/js/path/bin',
            'JSCFGDIR': '/root/optvar//cfg',
            'CODEDIR': '/root/opt/code/',
            'GODIR': '/root/optvar/go/',
            'HOMEDIR': '/root',
            'HRDDIR': '/root/optvar//hrd',
            'JSLIBDIR': '/js/path/lib/JumpScale/',
            'LIBDIR': '/js/path/lib/',
            'LOGDIR': '/root/optvar//log',
            'optDir': '/root/opt/',
            'PIDDIR': '/root/optvar//pid',
            'TMPDIR': '/root/optvar//tmp',
            'TEMPLATEDIR': '/js/path/templates',
            'VARDIR': '/root/optvar/'
        }
        result = self.core.dir_paths
        self.assertEqual(result, expected_result)
        mac_mock.assert_called_once_with()

    @unittest.skip("Needs fixing")
    def test_args_replace(self):
        """
        Test args replace
        """
        with patch("JumpScale.j") as j_mock:
            from JumpScale import j
            import JumpScale.tools.cuisine.CuisineCore
            JumpScale.tools.cuisine.CuisineCore.j = j
            from JumpScale.tools.cuisine.CuisineCore import CuisineCore
            executor_mock = MagicMock()
            j.tools.executor.getLocal.return_value = executor_mock
            executor = j.tools.executor.getLocal()
            cuisine = j.tools.cuisine.local
            cuisine_core = CuisineCore(executor, cuisine)
            cuisine_core.getenv = MagicMock()
            cuisine_core.getenv.return_value = self.dump_env
            cuisine_core.run = MagicMock()
            cuisine_core.run.return_value = (0, 'hostname', '')
            input_text = "$BASEDIR:$JSAPPSDIR:$TEMPLATEDIR:$VARDIR:$BINDIR:$CODEDIR:$JSCFGDIR:$HOMEDIR:$JSLIBDIR:$LIBDIR:$LOGDIR:$PIDDIR:$TMPDIR:$hostname"
            expected_output = "/opt/jumpscale8/:/opt/jumpscale8//apps:/opt/jumpscale8//templates:/optvar/:/opt/jumpscale8//bin:/opt/code/:/optvar//cfg:/root:/opt/jumpscale8//lib/JumpScale/:/opt/jumpscale8//lib/:/optvar//log:/optvar//pid:/optvar//tmp:hostname"
            actual_output = cuisine_core.args_replace(input_text)
            self.assertEqual(expected_output, actual_output)

    @unittest.skip("Needs fixing")
    def test_file_get_tmp_path(self):
        """
        Test file get tmp path
        """
        with mock.patch("JumpScale.j") as j_mock:
            from JumpScale import j
            import JumpScale.tools.cuisine.CuisineCore
            JumpScale.tools.cuisine.CuisineCore.j = j
            from JumpScale.tools.cuisine.CuisineCore import CuisineCore
            executor_mock = mock.MagicMock()
            j.tools.executor.getLocal.return_value = executor_mock
            executor = j.tools.executor.getLocal()
            cuisine = j.tools.cuisine.local
            cuisine_core = CuisineCore(executor, cuisine)
            cuisine_core.run = mock.MagicMock()
            cuisine_core.run.return_value = (0, 'hostname', '')
            cuisine_core.getenv = mock.MagicMock()
            cuisine_core.getenv.return_value = self.dump_env
            j.data.idgenerator.generateXCharID.return_value = 10 * 'a'
            expected_output = '/optvar//tmp/aaaaaaaaaa'
            actual_output = cuisine_core.file_get_tmp_path()
            self.assertEquals(expected_output, actual_output)
            expected_output = '/optvar//tmp/path'
            actual_output = cuisine_core.file_get_tmp_path(basepath="path")
            self.assertEquals(expected_output, actual_output)

    @unittest.skip("Needs fixing")
    def test_file_download(self):
        """
        Test file download
        """
        with mock.patch("JumpScale.j") as j_mock:
            from JumpScale import j
            import JumpScale.tools.cuisine.CuisineCore
            JumpScale.tools.cuisine.CuisineCore.j = j
            from JumpScale.tools.cuisine.CuisineCore import CuisineCore
            executor_mock = mock.MagicMock()
            j.tools.executor.getLocal.return_value = executor_mock
            executor = j.tools.executor.getLocal()
            cuisine = j.tools.cuisine.local
            cuisine_core = CuisineCore(executor, cuisine)
            url = 'http://hallo.com/downloadme.txt'
            to = '/tmp/path'
            cuisine_core.file_exists = mock.MagicMock()
            cuisine_core.file_exists.return_value = False
            cuisine_core.createDir = mock.MagicMock()
            cuisine_core.file_unlink = mock.MagicMock()
            cuisine_core.run = mock.MagicMock()
            cuisine_core.run.side_effect = [(33, '', 'err'), (0, 'Ok', '')]
            cuisine_core.touch = mock.MagicMock()
            cuisine_core.file_download(url, to)
            self.assertTrue(cuisine_core.touch.called)
            self.assertFalse(j.sal.fs.getBaseName.called)

    @unittest.skip("Needs fixing")
    def test_file_download_fail(self):
        """
        Test file download wth failure
        """
        with mock.patch("JumpScale.j") as j_mock:
            from JumpScale import j
            import JumpScale.tools.cuisine.CuisineCore
            JumpScale.tools.cuisine.CuisineCore.j = j
            from JumpScale.tools.cuisine.CuisineCore import CuisineCore
            from JumpScale.core.errorhandling import JSExceptions
            executor_mock = mock.MagicMock()
            j.tools.executor.getLocal.return_value = executor_mock
            executor = j.tools.executor.getLocal()
            cuisine = j.tools.cuisine.local
            cuisine_core = CuisineCore(executor, cuisine)
            url = 'http://hallo.com/downloadme.txt'
            to = '/tmp/path'
            cuisine_core.file_exists = mock.MagicMock()
            cuisine_core.file_exists.return_value = False
            cuisine_core.createDir = mock.MagicMock()
            cuisine_core.file_unlink = mock.MagicMock()
            cuisine_core.run = mock.MagicMock()
            cuisine_core.run.side_effect = [(32, '', 'err'), (0, 'Ok', '')]
            cuisine_core.touch = mock.MagicMock()
            j.exceptions.RuntimeError = JSExceptions.RuntimeError
            self.assertRaises(JSExceptions.RuntimeError, cuisine_core.file_download, url, to)

    @unittest.skip("Needs fixing")
    def test_file_expand(self):
        """
        Test file expand
        """
        with mock.patch("JumpScale.j") as j_mock:
            from JumpScale import j
            import JumpScale.tools.cuisine.CuisineCore
            JumpScale.tools.cuisine.CuisineCore.j = j
            from JumpScale.tools.cuisine.CuisineCore import CuisineCore
            executor_mock = mock.MagicMock()
            j.tools.executor.getLocal.return_value = executor_mock
            executor = j.tools.executor.getLocal()
            cuisine = j.tools.cuisine.local
            cuisine_core = CuisineCore(executor, cuisine)
            path = '/tmp/file.tgz'
            to = '/tmp/dest'
            cuisine_core.run = mock.MagicMock()
            cuisine_core.args_replace = mock.MagicMock()
            cuisine_core.file_expand(path, to)

    @unittest.skip("Needs fixing")
    def test_file_expand_fail(self):
        """
        Test file expand failure case
        """
        with mock.patch("JumpScale.j") as j_mock:
            from JumpScale import j
            import JumpScale.tools.cuisine.CuisineCore
            JumpScale.tools.cuisine.CuisineCore.j = j
            from JumpScale.tools.cuisine.CuisineCore import CuisineCore
            from JumpScale.core.errorhandling import JSExceptions
            executor_mock = mock.MagicMock()
            j.tools.executor.getLocal.return_value = executor_mock
            executor = j.tools.executor.getLocal()
            cuisine = j.tools.cuisine.local
            cuisine_core = CuisineCore(executor, cuisine)
            path = '/tmp/file.txt'
            to = '/tmp/dest'
            cuisine_core.run = mock.MagicMock()
            cuisine_core.args_replace = mock.MagicMock()
            cuisine_core.args_replace.side_effect = (path, to)
            j.exceptions.RuntimeError = JSExceptions.RuntimeError
            self.assertRaises(JSExceptions.RuntimeError, cuisine_core.file_expand, path, to)

    @unittest.skip("Needs fixing")
    def test_touch(self):
        """
        Test touch
        """
        with mock.patch("JumpScale.j") as j_mock:
            from JumpScale import j
            import JumpScale.tools.cuisine.CuisineCore
            JumpScale.tools.cuisine.CuisineCore.j = j
            from JumpScale.tools.cuisine.CuisineCore import CuisineCore
            executor_mock = mock.MagicMock()
            j.tools.executor.getLocal.return_value = executor_mock
            executor = j.tools.executor.getLocal()
            cuisine = j.tools.cuisine.local
            cuisine_core = CuisineCore(executor, cuisine)
            cuisine_core.run = mock.MagicMock()
            cuisine_core.args_replace = mock.MagicMock()
            cuisine_core.file_write = mock.MagicMock()
            self.assertIsNone(cuisine_core.touch('/tmp/hello'))
            self.assertTrue(cuisine_core.file_write.called)

    # def file_upload_binary(self, local, remote):
    # def file_upload_local(self, local, remote):
    # def file_download_binary(self, local, remote):
    # def file_download_local(self,remote, local):
    # def file_copy(self, source, dest, recursive=False, overwrite=False):
    # def file_move(self, source, dest, recursive=False):
    # def joinpaths(self, *args):
    # def find(self,path,recursive=True,pattern="",findstatement="",type="",contentsearch="",extendinfo=False):
    # def sudo(self, cmd, die=True,showout=True):
    # def run(self,cmd,die=True,debug=None,checkok=False,showout=True,profile=False,replaceArgs=True,check_is_ok=False):
    # def run_script(self,content,die=True,profile=False):
    # def command_location(self,command):
    # def tmux_execute_jumpscript(self,script,sessionname="ssh", screenname="js"):
    # def execute_jumpscript(self,script):
    # def execute_jumpscript(self,script):
