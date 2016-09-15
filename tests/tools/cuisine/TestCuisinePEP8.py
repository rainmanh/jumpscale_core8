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

    @patch('JumpScale.j.clients.git')
    @patch('JumpScale.j.tools.cuisine.local.core')
    def test_prepare_no_args_single_repo(self, core_mock, git_mock, pip_mock):
        """Happy Path: Test if parepare method called with no args, and one git repo found"""
        git_mock.find.return_value = [GitClientStub('/root')]
        self.pep8.prepare()
        pip_mock.install.assert_called_once_with('autopep8')
        core_mock.file_write.assert_called_once_with('/root/.git/hooks/pre-commit', self.hook_cmd)

    @patch('JumpScale.j.clients.git')
    @patch('JumpScale.j.tools.cuisine.local.core')
    def test_prepare_no_args_multiple_repos(self, core_mock, git_mock, pip_mock):
        """Happy Path: Test if parepare method called with no args, and multiple git repos found"""
        git_mock.find.return_value = [GitClientStub('/'), GitClientStub('/root')]
        self.pep8.prepare()
        pip_mock.install.assert_called_once_with('autopep8')
        self.assertEqual(core_mock.file_write.call_count, 2)

    @patch('JumpScale.j.tools.cuisine.local.core')
    def test_prepare_repo_path_provided(self, core_mock, pip_mock):
        """Happy Path: Test if parepare method called with a repo_path"""
        self.pep8.prepare('/root')
        pip_mock.install.assert_called_once_with('autopep8')
        core_mock.file_write.assert_called_once_with('/root/.git/hooks/pre-commit', self.hook_cmd)

    @patch('JumpScale.j.clients.git')
    def test_autopep8_no_args_single_repo(self, git_mock, pip_mock):
        """Happy Path: Test if autopep8 method called with no args, and one git repo found"""
        git_mock.find.return_value = [GitClientStub('/root')]
        self.pep8.autopep8()
        pip_mock.install.assert_called_once_with('autopep8')
