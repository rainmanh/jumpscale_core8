# Cuisine

The JumpScale implementation of Cuisine is a fork of the original Cuisine as available on GitHub: <https://github.com/sebastien/cuisine>

Cuisine provides [Chef](https://en.wikipedia.org/wiki/Chef_(software)-like funcionality for [Fabric](http://www.fabfile.org/).

Cuisine makes it easy to automate server installations and create configuration recipes by wrapping common administrative tasks, such as installing packages and creating users and groups, in Python functions.

Cuisine takes an `executor` object as an argument, though wich you connect locally or remotelly.

## Local

```python
executor = j.tools.executor.getLocal()
cuisine = j.tools.cuisine.get(executor)
# or simply j.tools.cuisine.local
```

## Remote

```python
executor = j.tools.executor.getSSHBased(addr, port, login,passwd)
cuisine = j.tools.cuisine.get(executor)
```

## Cuisine Modules

- [cuisine.core](cuisine.core.md)
- [cuisine.bash](cuisine.bash.md)
- [cuisine.pip](cuisine.pip.md)
- [cuisine.processmanager](cuisine.processmanager.md)
- [cuisine.apps](cuisine.apps.md)
- [cuisine.tmux](cuisine.tmux.md)
- [cuisine.docker](cuisine.docker.md)
- [cuisine.ssh](cuisine.ssh.md)
- [cuisine.package](cuisine.package.md)
- [cuisine.installer](cuisine.installer.md)
- [cuisine.installerdevelop](cuisine.installerdevelop.md)
