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
