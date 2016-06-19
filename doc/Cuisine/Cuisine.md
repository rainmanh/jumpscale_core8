
## Cuisine

A set of very nice tools to do basic system management to a node.
This is all based on https://github.com/sebastien/cuisine 

Cuisine takes an executor object as an argument. Examples of executors are local executor and ssh executor.

### for a local connection

```py
executor = j.tools.executor.getLocal()
cuisine = j.tools.cuisine.get(executor)
# or simply j.tools.cuisine.local
```

###for a remote connection

```py
executor = j.tools.executor.getSSHBased(addr, port, login,passwd)
cuisine = j.tools.cuisine.get(executor)
```

### More info about cuisine

Cuisine makes it easy to write automatic server installation and configuration recipes by wrapping common administrative tasks (installing packages, creating users and groups) in Python functions.

Cuisine is designed to work with Fabric and provide all you need for getting your new server up and running in minutes.


##Core

Cuisine core module (`cuisine.core`) handles basic fs operations and command execution.

Examples for methods inside core:

* command_check: tests if the given command is available on the system.
* command_ensure: ensures that the given command is present, if not installs the package with the given name, which is the same as the command by default.
* createDir: to create a directory.
* execute_python: execute a python script (script as content) in a remote tmux command, the stdout will be returned.
* execute_jumpscript: execute a jumpscript (script as content) in a remote tmux command, the stdout will be returned.
* file_append: appends the given content to the remote file at the given location.
* file_read: read the content of a file.* file_copy: copy a file.
* file_write: write the content to a file.
* isArch, isDocker, isMac, isLxc, isUbuntu: check for the target os.
* run: run a command.
```py
cuisine.run('ls')
cuisine.run('false', die=False) //it won't raise an error
```
* run_script: run a script.
  `cuisine.run_sctipt('cd /\npwd'`
* sudo: run a command using sudo.
  `cuisine.sudo('apt-get  install httpie')`
* args_replace: replace arguments inside commands and paths such as `$binDir`, `$hostname`, `$codeDir`, `$tmpDir`.
  `cuisine.arg_replace('$binDir/python -c "print(1)"')`

##Bash

`cuisine.bash` handles environment variables.

## PIP

`cuisine.pip` handles python package management

Examples for methods inside pip:

* install: to install a python package.
  `cuisine.pip.install('pygments')`
* multiInstall: install multiple python packages. The packages are passed as a newline separated string, with a hash at the beginning of the packages to be skipped.
```
cuisine.pip.multiInstall("""flask
pygments""")
```
* remove: to remove a package.
  `cuisine.pip.remove('pygments')`
* upgrade: to upgrade a package.
  `cuisine.pip.upgrade('pygments')`

## Process Manager

`cuisine.processmanager` handles process management.
It's used to check for a process manager in the target machine, and if it finds one it will use it; otherwise it will fall back to spawning the process in `tmux`.

You can force using a certain process manager using `cuisine.processmanager.get(name)` and pass name as a string. and that will fail in case that the process manager is not supported in the target machine.

Examples for methods inside processmanager:

* ensure: this is to register the process in the first time, or to ensure that it's running. For the first time you have to pass the name of the process and the command to be executed for the process and optionally the `cwd` and the environment variables. Later you can only call it using the name argument.
* start: to start a certain process.
* stop: stop a certain process.
* list: list all processes.
* startAll: start all recognized processes.

### Currently supported process managers:

#### Systemd

Systemd is a process manager that uses a util `systemctl` to start and stop services.
Systemd keep strack of a service by keeping a `.service` file under `/etc/systemd/system/`.

#### RunIt

RunIt is a process manager tath uses a util `sv` to start and stop services.
RunIt keeps track of services by keeping a directory with the name of the service under `/etc/service/`, the directory has an executable file run. that gets executed by the shell to bootstrap the service.

#### Tmux

Tmux is the default process manager. The process manager module uses it in case that there is no other available process manager in the target system that is supported.

Tmux doesn't keep track of the services, and that is whythe process manager module stores service information in a hash map in redis called `processcmds`.

Starting a service is done by simple opening a window in tmux with the name of the service and starting the service in it. And stopping a service is done by closing the window with that name.

## Apps

`cuisine.apps` handles application management.

Examples for methods inside an application:

* build: for building the application on the specified target, it takes arguments needed for building and an optional start kwarg for starting the application after building it.
* start: to start the application.
* stop: to stop the application.

### Applications that are currently supported

```
cockpit
controller (g8os controller)
core (g8os core)
deployerbot
etcd
fs (g8way FileSystem)
grafana
influxdb
mongodb
portal
redis
skydns
stor
syncthing
vulcand
weave
```

## Tmux

`cuisine.tmux` is a client for tmux

Examples for methods inside tmux:

* attachSession: attach to a running session.
* configure: write the default tmux configuration.
* createSession: create a new tmux session.
* createWindow: create a window in a session.
* executeInScreen: execute a command.
* getSessions: list the running sessions.
* getWindows: list the running windows in a session.
* killSession: kill a session.
* killSessions: kill all sessions.
* killWindow: kill a window.
* logWindow: store the stdout of a window in a file.
* windowExists: check if a window exist.

Example:

```py
tmux = j.tools.cuisine.local.tmux
tmux.createSession('s1', ['w1', 'w2'])
tmux.executeInScreen('s1', 'w1', 'ping 8.8.8.8')
tmux.executeInScreen('s1', 'w2', 'python3 -m http.server')
tmux.killSession('s1')
```

## Docker

`cuisine.docker` is a client for docker

Examples for methods inside docker:

* install: installs docker and docker compose.
* archBuild: build an arch docker.
* ubuntuBuild: build an ubuntu docker.
* archSysstemd: build an arch docker with systemd as a process manager.
* ubuntuSystemd: build an ubuntu docker with systemd as a process manager.

## SSH

`cuisine.ssh` to handle remote ssh management.

Examples for methods inside ssh:

* authorize: ldds the given key to the '.ssh/authorized_keys' for the given user.
* enableAccess: lake sure we can access the environment keys are a list of ssh pub keys.
* keygen: lenerates a pair of ssh keys in the user's home .ssh directory.
* scan: lcan a range of ips for an runnig ssh server.
* sshagent_add: ldd a pair of keys to a runnig ssh agent.
* sshagent_remove: lemove a pair of keys to a runnig ssh agent.
* test_login: lest ssh login for a range of ips using a password.
* test_login_pushkey: lest ssh login for a range of ips using a public key.      
* unauthorize: lemoves the given key from the remote '.ssh/authorized_keys' for the given user.
* unauthorizeAll: lemove every key from the remote '.ssh/authorized_keys'.

## Package

`cuisine.package` for dealing with package managers.

Examples for methods inside package:

* clean: clean packaging system e.g. remove outdated packages & caching packages. 
* ensure: ensure a package is installed.
* install: install a package. 
* mdupdate: update metadata of system.
* multiInstall: install packages passsed as packagelist which is a text file and each line is a name of the package.
* remove: remove a package.
* start: start the service of the package.
* update: update a certain package.
* upgrade: upgrades system, passing distupgrade=True will make a distribution upgrade.

## Installer

`cuisine.installer` is responsible for installing jumpscale8 in a sandbox mode. It contains a method `jumpscale8` which uses `aysfs` to get jumpscale to the target machine. (warning: it removes everything under /opt).

`cuisine.installer.jumpscale8` takes two parameters:

1. rw: to mount the fs as read-write. defaults to False.
2. reset: reinstall jumpscale even if it exists. defaults to False. 

## InstallerDevelop

`cuisine.installerdevelop` is responsible for installing jumpscale8 in development mode. It contains a method `jumpscale8` to do that locally.

