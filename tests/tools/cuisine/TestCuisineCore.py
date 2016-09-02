"""
Test CuisineCore module
"""
import unittest
from unittest import mock

class TestCuisineCore(unittest.TestCase):

    def setUp(self):
        self.dump_env = {
            'HOME': '/root',
            'HOSTNAME': 'js8-core',
            'JSBASE': '/opt/jumpscale8/',
            'LD_LIBRARY_PATH': '/opt/jumpscale8//bin',
            'LESSCLOSE': '/usr/bin/lesspipe %s %s',
            'LESSOPEN': '| /usr/bin/lesspipe %s',
            'LS_COLORS': 'rs=0:di=01;34:ln=01;36:mh=00:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:mi=00:su=37;41:sg=30;43:ca=30;41:tw=30;42:ow=34;42:st=37;44:ex=01;32:*.tar=01;31:*.tgz=01;31:*.arc=01;31:*.arj=01;31:*.taz=01;31:*.lha=01;31:*.lz4=01;31:*.lzh=01;31:*.lzma=01;31:*.tlz=01;31:*.txz=01;31:*.tzo=01;31:*.t7z=01;31:*.zip=01;31:*.z=01;31:*.Z=01;31:*.dz=01;31:*.gz=01;31:*.lrz=01;31:*.lz=01;31:*.lzo=01;31:*.xz=01;31:*.bz2=01;31:*.bz=01;31:*.tbz=01;31:*.tbz2=01;31:*.tz=01;31:*.deb=01;31:*.rpm=01;31:*.jar=01;31:*.war=01;31:*.ear=01;31:*.sar=01;31:*.rar=01;31:*.alz=01;31:*.ace=01;31:*.zoo=01;31:*.cpio=01;31:*.7z=01;31:*.rz=01;31:*.cab=01;31:*.jpg=01;35:*.jpeg=01;35:*.gif=01;35:*.bmp=01;35:*.pbm=01;35:*.pgm=01;35:*.ppm=01;35:*.tga=01;35:*.xbm=01;35:*.xpm=01;35:*.tif=01;35:*.tiff=01;35:*.png=01;35:*.svg=01;35:*.svgz=01;35:*.mng=01;35:*.pcx=01;35:*.mov=01;35:*.mpg=01;35:*.mpeg=01;35:*.m2v=01;35:*.mkv=01;35:*.webm=01;35:*.ogm=01;35:*.mp4=01;35:*.m4v=01;35:*.mp4v=01;35:*.vob=01;35:*.qt=01;35:*.nuv=01;35:*.wmv=01;35:*.asf=01;35:*.rm=01;35:*.rmvb=01;35:*.flc=01;35:*.avi=01;35:*.fli=01;35:*.flv=01;35:*.gl=01;35:*.dl=01;35:*.xcf=01;35:*.xwd=01;35:*.yuv=01;35:*.cgm=01;35:*.emf=01;35:*.ogv=01;35:*.ogx=01;35:*.aac=00;36:*.au=00;36:*.flac=00;36:*.m4a=00;36:*.mid=00;36:*.midi=00;36:*.mka=00;36:*.mp3=00;36:*.mpc=00;36:*.ogg=00;36:*.ra=00;36:*.wav=00;36:*.oga=00;36:*.opus=00;36:*.spx=00;36:*.xspf=00;36:',
            'PATH': '/opt/jumpscale8//bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
            'PWD': '/opt/code/github/jumpscale/jumpscale_core8',
            'PYTHONPATH': '.:/opt/jumpscale8//lib:/opt/jumpscale8//lib/lib-dynload/:/opt/jumpscale8//bin:/opt/jumpscale8//lib/python.zip:/opt/jumpscale8//lib/plat-x86_64-linux-gnu:',
            'PYTHONUNBUFFERED': '1',
            'SHLVL': '2',
            'TERM': 'xterm',
            '_': '/usr/bin/printenv',
            '_OLD_LDLIBRARY_PATH': '',
            '_OLD_PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
            '_OLD_PS1': '',
            '_OLD_PYTHONPATH': ''
        }

    def tearDown(self):
        pass


    def test_create_cuisine_core(self):
        """
        Test creating CuisineCore instance
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


    def test_reset_actions(self):
        """
        Test reset actions
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
            cuisine_core.reset_actions()
            self.assertTrue(j.actions.reset.called)

    def test_id_property(self):
        """
        Test accessing the id property
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
            self.assertIsNotNone(cuisine_core.id)

    def test_isJS8Sandbox_property(self):
        """
        Test accessing the isJS8Sandbox property
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
            self.assertIsNotNone(cuisine_core.isJS8Sandbox)

    def test_dir_paths_property(self):
        """
        Test accessing the dir_paths property
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
            cuisine_core.getenv = mock.MagicMock()
            cuisine_core.getenv.return_value = self.dump_env
            self.assertIsNotNone(cuisine_core.dir_paths)


    def test_args_replace(self):
        """
        Test args replace
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
            cuisine_core.getenv = mock.MagicMock()
            cuisine_core.getenv.return_value = self.dump_env
            cuisine_core.run = mock.MagicMock()
            cuisine_core.run.return_value = (0, 'hostname', '')
            input_text = "$base:$appDir:$tmplsDir:$varDir:$binDir:$codeDir:$cfgDir:$homeDir:$jsLibDir:$libDir:$logDir:$pidDir:$tmpDir:$hostname"
            expected_output = "/opt/jumpscale8/:/opt/jumpscale8//apps:/opt/jumpscale8//templates:/optvar/:/opt/jumpscale8//bin:/opt/code/:/optvar//cfg:/root:/opt/jumpscale8//lib/JumpScale/:/opt/jumpscale8//lib/:/optvar//log:/optvar//pid:/optvar//tmp:hostname"
            actual_output = cuisine_core.args_replace(input_text)
            self.assertEqual(expected_output, actual_output)

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
            cuisine_core.run.return_value = 'hostname'
            cuisine_core.getenv = mock.MagicMock()
            cuisine_core.getenv.return_value = self.dump_env
            j.data.idgenerator.generateXCharID.return_value = 10*'a'
            expected_output = '/optvar//tmp/aaaaaaaaaa'
            actual_output = cuisine_core.file_get_tmp_path()
            self.assertEquals(expected_output, actual_output)
            expected_output = '/optvar//tmp/path'
            actual_output = cuisine_core.file_get_tmp_path(basepath="path")
            self.assertEquals(expected_output, actual_output)

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
            cuisine_core.run.side_effect = [(33, '', 'err'),(0, 'Ok', '')]
            cuisine_core.touch = mock.MagicMock()
            cuisine_core.file_download(url, to)
            self.assertTrue(cuisine_core.touch.called)
            self.assertFalse(j.sal.fs.getBaseName.called)

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
            cuisine_core.run.side_effect = [(32, '', 'err'),(0, 'Ok', '')]
            cuisine_core.touch = mock.MagicMock()
            j.exceptions.RuntimeError = JSExceptions.RuntimeError
            self.assertRaises(JSExceptions.RuntimeError, cuisine_core.file_download, url, to)

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
    # def fs_find(self,path,recursive=True,pattern="",findstatement="",type="",contentsearch="",extendinfo=False):
    # def sudo(self, cmd, die=True,showout=True):
    # def run(self,cmd,die=True,debug=None,checkok=False,showout=True,profile=False,replaceArgs=True,check_is_ok=False):
    # def run_script(self,content,die=True,profile=False):
    # def command_location(self,command):
    # def tmux_execute_jumpscript(self,script,sessionname="ssh", screenname="js"):
    # def execute_jumpscript(self,script):
    # def execute_jumpscript(self,script):
