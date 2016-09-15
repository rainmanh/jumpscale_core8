from os import path
from JumpScale import j

base = j.tools.cuisine._getBaseClass()


class CuisinePEP8(base):

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def prepare(self):
        """ Install pre-commit hook to run autopep8 """
        repos = j.clients.git.find()
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

    def autopep8(self, repo_path=None, commit=True):
        """ Run autopep8 on found repos and commit with pep8 massage """
        repos = j.clients.git.find() if repo_path is None else [repo_path]
        paths = (repo[-1] for repo in repos)
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
            git fetch
            branch=$(git symbolic-ref --short -q HEAD)
            git rebase origin/$branch
        fi
        """

        cmd = pep8_cmd if not commit else pep8_cmd + commit_cmd
        for repo_path in paths:
            self._cuisine.core.execute_script(cmd.format(repo_path), tmux=False, die=False)
