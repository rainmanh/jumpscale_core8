"""
Test CuisinePEP8 module
"""
import unittest
from unittest.mock import patch

from JumpScale import j


class GitClientStub:

    def __init__(self, baseDir):
        self.baseDir = baseDir


@patch('JumpScale.j.tools.cuisine.local.development.pip')
@patch('JumpScale.j.clients.git')
class TestCuisineCore(unittest.TestCase):

    def setUp(self):
        self.pep8 = j.tools.cuisine.local.development.pep8
        self.hook_cmd = """
        #!/bin/sh
        touched_python_files=`git diff --cached --name-only |egrep '\.py$' || true`
        if [ -n "$touched_python_files" ]; then
            autopep8 -ria --max-line-length=120 $touched_python_files
            git add $touched_python_files
        fi
        """

        self.pep8_cmd = """
        #!/bin/bash
        cd /root
        autopep8 -ria --max-line-length=120 .
        """
        self.commit_cmd = """
        touched_python_files=`git diff --name-only |egrep '\.py$' || true`
        if [ -n "$touched_python_files" ]; then
            git add .
            git commit -m 'pep8'
        fi
        """
        self.rebase_cmd = """
        git fetch
        branch=$(git symbolic-ref --short -q HEAD)
        git rebase origin/$branch
        """

    @patch('JumpScale.j.tools.cuisine.local.core')
    def test_prepare_no_args_single_repo(self, core_mock, git_mock, pip_mock):
        """Happy Path: Test if parepare method called with no args, and one git repo found"""
        git_mock.find.return_value = [GitClientStub('/root')]
        self.pep8.prepare()
        pip_mock.install.assert_called_once_with('autopep8')
        core_mock.file_write.assert_called_once_with('/root/.git/hooks/pre-commit', self.hook_cmd)

    @patch('JumpScale.j.tools.cuisine.local.core')
    def test_prepare_no_args_multiple_repos(self, core_mock, git_mock, pip_mock):
        """Happy Path: Test if parepare method called with no args, and multiple git repos found"""
        git_mock.find.return_value = [GitClientStub('/'), GitClientStub('/root')]
        self.pep8.prepare()
        pip_mock.install.assert_called_once_with('autopep8')
        self.assertEqual(core_mock.file_write.call_count, 2)

    @patch('JumpScale.j.tools.cuisine.local.core')
    def test_prepare_repo_path_provided(self, core_mock, git_mock, pip_mock):
        """Happy Path: Test if parepare method called with a repo_path"""
        self.pep8.prepare('/root')
        pip_mock.install.assert_called_once_with('autopep8')
        core_mock.file_write.assert_called_once_with('/root/.git/hooks/pre-commit', self.hook_cmd)

    @patch('JumpScale.j.tools.cuisine.local.core')
    def test_autopep8_no_args_single_repo(self, core_mock, git_mock, pip_mock):
        """Happy Path: Test if autopep8 method called with no args, and one git repo found"""
        git_mock.find.return_value = [GitClientStub('/root')]
        self.pep8.autopep8()
        core_mock.execute_script.assert_called_once_with(self.pep8_cmd + self.commit_cmd, tmux=False, die=False)
        pip_mock.install.assert_called_once_with('autopep8')

    @patch('JumpScale.j.tools.cuisine.local.core')
    def test_autopep8_no_args_multiple_repos(self, core_mock, git_mock, pip_mock):
        """Happy Path: Test if autopep8 method called with no args, and multiple git repo found"""
        git_mock.find.return_value = [GitClientStub('/root'), GitClientStub('/test')]
        self.pep8.autopep8()
        self.assertEqual(core_mock.execute_script.call_count, 2)
        pip_mock.install.assert_called_once_with('autopep8')

    @patch('JumpScale.j.tools.cuisine.local.core')
    def test_autopep8_no_args_commit_false(self, core_mock, git_mock, pip_mock):
        """Happy Path: Test if autopep8 method called if commit is false"""
        git_mock.find.return_value = [GitClientStub('/root')]
        self.pep8.autopep8(commit=False)
        core_mock.execute_script.assert_called_once_with(self.pep8_cmd, tmux=False, die=False)
        pip_mock.install.assert_called_once_with('autopep8')

    @patch('JumpScale.j.tools.cuisine.local.core')
    def test_autopep8_no_args_commit_false_rebase_true(self, core_mock, git_mock, pip_mock):
        """Happy Path: Test if autopep8 method called if commit is false and rebase is true"""
        git_mock.find.return_value = [GitClientStub('/root')]
        self.pep8.autopep8(commit=False, rebase=True)
        core_mock.execute_script.assert_called_once_with(self.pep8_cmd, tmux=False, die=False)
        pip_mock.install.assert_called_once_with('autopep8')

    @patch('JumpScale.j.tools.cuisine.local.core')
    def test_autopep8_no_args_commit_true_rebase_true(self, core_mock, git_mock, pip_mock):
        """Happy Path: Test if autopep8 method called if commit is true and rebase is true"""
        git_mock.find.return_value = [GitClientStub('/root')]
        self.pep8.autopep8(rebase=True)
        core_mock.execute_script.assert_called_once_with(
            self.pep8_cmd + self.commit_cmd + self.rebase_cmd,
            tmux=False,
            die=False
        )
        pip_mock.install.assert_called_once_with('autopep8')

    @patch('JumpScale.j.tools.cuisine.local.core')
    def test_autopep8_if_repo_path_passed(self, core_mock, git_mock, pip_mock):
        """Happy Path: Test if autopep8 method called with repo_path"""
        self.pep8.autopep8('/root')
        core_mock.execute_script.assert_called_once_with(self.pep8_cmd + self.commit_cmd, tmux=False, die=False)
        pip_mock.install.assert_called_once_with('autopep8')
