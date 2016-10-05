<!-- toc -->
## j.tools.cuisine.local.development.pep8

- /opt/jumpscale8/lib/JumpScale/tools/cuisine/development/CuisinePEP8.py

### Methods

#### autopep8(*repo_path, commit=True, rebase*) 

```
Run autopep8 on found repos and commit with pep8 massage
@param repo_path: path of desired repo to autopep8, if None will find all recognized repos
    to jumpscale
@param commit: commit with pep8 as the commit message

```

#### prepare(*repo_path*) 

```
Install pre-commit hook to run autopep8

```

