from os import path
from JumpScale import j

base = j.tools.cuisine._getBaseClass()


class CuisinePEP8(base):

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def prepare(self, repo_path=None):
        """ Install pre-commit hook to run autopep8 """
        j.tools.cuisine.local.development.pip.install('autopep8')

        # Get git repos paths
        repos = j.clients.git.find() if repo_path is None else [repo_path]
        paths = (path.join(repo[-1], '.git/hooks/pre-commit') for repo in repos)

        pre_commit_cmd = """
        #!/bin/sh
        touched_python_files=`git diff --cached --name-only |egrep '\.py$' || true`
        if [ -n "$touched_python_files" ]; then
            autopep8 -ria --max-line-length=120 $touched_python_files
            git add $touched_python_files
        fi
        """
        for repo_path in paths:
            self._cuisine.core.file_write(repo_path, pre_commit_cmd)

    def autopep8(self, repo_path=None, commit=True, rebase=True):
        """
        Run autopep8 on found repos and commit with pep8 massage
        @param repo_path: path of desired repo to autopep8, if None will find all recognized repos to jumpscale
        @param commit: commit with pep8 as the commit message
        """
        j.tools.cuisine.local.development.pip.install('autopep8', upgrade=True)

        # Get git repos paths
        repos = j.clients.git.find() if repo_path is None else [repo_path]
        paths = (repo[-1] for repo in repos)

        # Prepare cmd command
        pep8_cmd = """
        #!/bin/bash
        cd {0}
        autopep8 -ria --max-line-length=120 .
        """
        commit_cmd = """
        touched_python_files=`git diff --name-only |egrep '\.py$' || true`
        if [ -n "$touched_python_files" ]; then
            git add .
            git commit -m 'pep8'
        fi
        """
        rebase_cmd = """
        git fetch
        branch=$(git symbolic-ref --short -q HEAD)
        git rebase origin/$branch
        """

        cmd = ""
        if commit is True:
            cmd = pep8_cmd + commit_cmd
            cmd += rebase_cmd if rebase else ''
        else:
            cmd = pep8_cmd

        # Execute cmd on paths
        for repo_path in paths:
            self._cuisine.core.execute_script(cmd.format(repo_path), tmux=False, die=False)
