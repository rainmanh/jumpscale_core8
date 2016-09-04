<!-- toc -->
## j.sal.unix

- /opt/jumpscale8/lib/JumpScale/sal/unix/Unix.py
- Properties
    - logger

### Methods

#### addCronJob(*commandToExecute, interval=1, logFilePath, replaceLineIfCommandAlreadyInCrontab=True, unit=1*) 

```
Add a cronjob to the system

@param commandToExecute: The command to execute
@type commandToExecute: string
@param interval: The interval at which to launch the commandToExecute
@type interval: number
@param logFilePath: the path of the logfile to redirect the output of crontab to
@type logFilePath: string
@param replaceLineIfCommandAlreadyInCrontab: Specifies whether to replace the line if a
    command already exists in crontab
@type replaceLineIfCommandAlreadyInCrontab: bool
@param unit: The unit of the interval
@type unit: TimeIntervalUnit

```

#### addSystemGroup(*groupname*) 

```
Add a group to the system

Note: you should be root to run this python command.

@param groupname: Name of the group to add
@type groupname : string

```

#### addSystemUser(*username, groupname, shell='/bin/bash', homedir*) 

```
Add a user to the system

Note: you should be root to run this python command.

@param username: Username of the user to add
@param groupname: Optional param to add user to existing systemgroup
@param shell: Optional param to specify the shell of the user
@type username: string

```

#### addUserToGroup(*username, groupname*) 

#### checkApplicationInstalled(*appname*) 

```
check if app is installed,  if yes return True

```

#### chmod(*root, mode, recurse, dirPattern='*', filePattern='*', dirs=True, files=True*) 

```
Chmod based on system.fs.walk

```

#### chown(*path, user, group, recursive*) 

```
Chown a file
@param path: the path of a file or a directory to be chown
@type path: string
@param user: username to be used as the new owner
@type user: string
@param group: groupname to be used as the new group owner (if None, then root is used as a
    groupname0
@type group: string
@param recursive: if path is a directory, all files underneath the path are also chown if
    True (default False)
@type recursive: boolean

```

#### chroot(*path*) 

```
Change root directory path

@param path: Path to chroot() to
@type path: string

```

#### crypt(*word, salt*) 

```
Return a string representing the one-way hash of a password, with a salt
prepended.

```

#### daemonize(*chdir='/', umask*) 

```
Daemonize a process using a double fork

This method will fork the current process to create a daemon process.
It will perform a double fork(2), chdir(2) to the given folder (or not
chdir at all if the C\{chdir\} argument is C\{None\}), and set the new
process umask(2) to the value of the C\{umask\} argument, or not reset
it if this argument is -1.

While forking, a setsid(2) call will be done to become session leader
and detach from the controlling TTY.

In the child process, all existing file descriptors will be closed,
including stdin, stdout and stderr, which will be re-opened to
/dev/null.

The method returns a tuple<bool, number>. If the first item is True,
the current process is the daemonized process. If it is False,
the current process is the process which called the C\{daemonize\}
method, which can most likely be closed now. The second item is the
PID of the current process.

@attention: Make sure you know really well what fork(2) does before using this method

@param chdir: Path to chdir(2) to after forking. Set to None to disable chdir'ing
@type chdir: string or None
@param umask: Umask to set after forking. Set to -1 not to set umask
@type umask: number

@returns: Daemon status and PID
@rtype: tuple<bool, number>

@raise RuntimeError: System does not support fork(2)

```

#### disableUnixUser(*username*) 

```
Disables a given unix user

@param username: Name of the user to disable
@type username: string

```

#### enableUnixUser(*username*) 

```
Enables a given unix user

@param username: Name of the user to enable
@type username: string

```

#### executeAsUser(*command, username, **kwargs*) 

```
Execute a given command as a specific user

When calling this method, the command will be wrapped inside 'su' to
be executed as some specific user. This requires the application which
spawns the command to be running as root.

Next to this, it behaves exactly as C\{j.sal.process.execute\},
including the same named arguments.

@param command: Command to execute
@type command: string
@param username: Name of the user to impersonate
@type username: string

@returns: Exit code and command output
@rtype: tuple

@raises RuntimeError: When the application is not running as root
@raises RuntimeError: If /bin/su is not available on the system
@raises ValueError: When the provided username can't be resolved

@see: jumpscale.system.process.SystemProcess.execute

```

#### executeDaemonAsUser(*command, username, **kwargs*) 

```
Execute a given command as a background process as a specific user

When calling this method, the command will be wrapped inside 'su' to
be executed as some specific user. This requires the application which
spawns the command to be running as root.

Next to this, it behaves exactly as C\{j.sal.process.runDaemon\},
including the same named arguments.

@param command: Command to execute
@type command: string
@param username: Name of the user to impersonate
@type username: string

@returns: pid of the process
@rtype: int

@raises RuntimeError: When the application is not running as root
@raises RuntimeError: If /bin/su is not available on the system
@raises ValueError: When the provided username can't be resolved

@see: jumpscale.system.process.runDaemon

```

#### getBashEnvFromFile(*file, var*) 

```
Get the value of an environment variable in a Bash file

@param file: Bash file defining the variable
@type file: string
@param var: Variable name
@type var: string

```

#### getMachineInfo() 

```
Get memory and CPU info about this machine

@returns: Amount of available memory, CPU speed and number of CPUs
@rtype: tuple

```

#### killGroup(*pid*) 

```
Kill a process group

killGroup will get the parent pid from the pid given and kill the group with signal
    SIGKILL (default)

@type pid: int
@param pid: process id

```

#### removeUnixUser(*username, removehome, die=True*) 

```
Remove a given unix user

@param username: Name of the user to remove
@type username: string

```

#### setUnixUserPassword(*username, password*) 

```
Set a password on unix user

@param username: Name of the user to enable
@type username: string

@param password: Password to set on the user
@type username: string

```

#### unixGroupExists(*groupname*) 

```
Checks if a given group already exists in the system

@param groupname: Name of the group to check for
@type groupname: string

@returns: Whether the group exists
@rtype: bool

```

#### unixUserExists(*username*) 

```
Checks if a given user already exists in the system

@param username: Username of the user to check for
@type username: string

@returns: Whether the user exists
@rtype: bool

```

#### unixUserIsInGroup(*username, groupname*) 

```
Checks if a given user is a member of the given group

@param username: Username to check for
@type username: string
@param groupname: Group to check for
@type groupname: string

@returns: Whether the user is a member of the group
@rtype: bool

```

