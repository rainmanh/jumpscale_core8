<!-- toc -->
## j.sal.process

- /opt/jumpscale8/lib/JumpScale/sal/process/SystemProcess.py
- Properties
    - logger

### Methods

#### appCheckActive(*appname*) 

#### appGetPids(*appname*) 

#### appGetPidsActive(*appname*) 

#### appNrInstances(*appname*) 

#### appNrInstancesActive(*appname*) 

#### appsGet() 

#### appsGetNames() 

#### checkProcessForPid(*pid, process*) 

```
Check whether a given pid actually does belong to a given process name.
@param pid: (int) the pid to check
@param process: (str) the process that should have the pid
@return status: (int) 0 when ok, 1 when not ok.

```

#### checkProcessRunning(*process, min=1*) 

```
Check if a certain process is running on the system.
you can specify minimal running processes needed.
@param process: String with the name of the process we
    are trying to check
@param min: (int) minimal threads that should run.
@return True if ok

```

#### checkstart(*cmd, filterstr, nrtimes=1, retry=1*) 

```
@param cmd is which command to execute to start e.g. a daemon
@param filterstr is what to check on if its running
@param nrtimes is how many processes need to run

```

#### checkstop(*cmd, filterstr, retry=1, nrinstances*) 

```
@param cmd is which command to execute to start e.g. a daemon
@param filterstr is what to check on if its running
@param nrtimes is how many processes need to run

```

#### execute(*command, die=True, outputToStdout, useShell, ignoreErrorOutput*) 

```
Executes a command, returns the exitcode and the output
@param command: command to execute
@param die: boolean to die if got non zero exitcode
@param outputToStdout: boolean to show/hide output to stdout
@param ignoreErrorOutput standard stderror is added to stdout in out result, if you want
    to make sure this does not happen put on True
@rtype: integer represents the exitcode plus the output of the executed command
if exitcode is not zero then the executed command returned with errors

```

#### executeAsync(*command, args, printCommandToStdout, redirectStreams=True, argsInCommand, useShell, outputToStdout=True*) 

```
Execute command asynchronous. By default, the input, output and error streams of the
    command will be piped to the returned Popen object. Be sure to call commands that
    don't expect user input, or send input to the stdin parameter of the returning Popen
    object.
@param command: Command to execute. (string)
@param args: [Optional, [] by default] Arguments to be passed to the command. (Array of
    string)
@param printCommandToStdOut: [Optional, False by default] Indicates if the command to be
    executed needs to be printed to screen. (boolean)
@param redirectStreams: [Optional, True by default] Indicates if the input, output and
    error streams should be captured by the returned Popen object. If not, the output and
    input will be mixed with the streams of the calling process. (boolean)
@param argsInCommand: [Optional, False by default] Indicates if the command-parameter
    contains command-line arguments.  If argsInCommand is False and args is not empty, the
    contents of args will be added to the command when executing.
@param useShell: [Optional, False by default on Windows, True by default on Linux]
    Indicates if the command should be executed throug the shell.
@return: If redirectStreams is true, this function returns a subprocess.Popen object
    representing the started process. Otherwise, it will return the pid-number of the
    started process.

```

#### executeCode(*code, params*) 

```
execute a method (python code with def)
use params=j.data.params.get() as input

```

#### executeInSandbox(*command, timeout*) 

```
Executes a command
@param command: string (command to be executed)
@param timeout: 0 means to ever, expressed in seconds

```

#### executeIndependant(*cmd*) 

#### executeScript(*scriptName*) 

```
execute python script from shell/Interactive Window

```

#### executeWithoutPipe(*command, die=True, printCommandToStdout*) 

```
Execute command without opening pipes, returns only the exitcode
This is platform independent
@param command: command to execute
@param die: boolean to die if got non zero exitcode
@param printCommandToStdout: boolean to show/hide output to stdout
@param outputToStdout: Deprecated. Use 'printCommandToStdout' instead.
@rtype: integer represents the exitcode
if exitcode is not zero then the executed command returned with errors

```

#### getDefunctProcesses() 

#### getEnviron(*pid*) 

#### getMyProcessObject() 

#### getPidsByFilter(*filterstr*) 

#### getPidsByPort(*port*) 

```
Returns pid of the process that is listening on the given port

```

#### getProcessByPort(*port*) 

```
Returns the full name of the process that is listening on the given port

@param port: the port for which to find the command
@type port: int
@return: full process name
@rtype: string

```

#### getProcessObject(*pid*) 

#### getProcessPid(*process*) 

#### getProcessPidsFromUser(*user*) 

#### getSimularProcesses() 

#### isPidAlive(*pid*) 

```
Checks whether this pid is alive.
For unix, a signal is sent to check that the process is alive.
For windows, the process information is retrieved and it is double checked that the
    process is python.exe
or pythonw.exe

```

#### kill(*pid, sig*) 

```
Kill a process with a signal
@param pid: pid of the process to kill
@param sig: signal. If no signal is specified signal.SIGKILL is used

```

#### killProcessByName(*name, sig*) 

#### killProcessByPort(*port*) 

#### killUserProcesses(*user*) 

#### run(*commandline, showOutput, captureOutput=True, maxSeconds, stopOnError=True, user, group, **kwargs*) 

```
Execute a command and wait for its termination

This function spawns a subprocess which executes the given command line in a
subshell. The function waits for the spawned process to terminate, or until
a time period of maxSeconds was exceeded.

When showOutput is set to True, stdin, stderr and stdout handles of the
subprocess are bound to the handles of the calling process. This can be used
to run interactive commands.

Both showOutput and captureOutput can't be True at the same time.

Any extra keyword arguments are passed to L\{subprocess.Popen\}. These
arguments can overwrite any argument set by this function, so setting any of
the arguments used by this function (including C\{stdin\}, C\{stdout\},
C\{stderr\}, C\{env\}, C\{shell\} and C\{preexec_fn\}) can change the behavior
of this function. This could e.g. be used to set C\{cwd\}.

The exit code contained in the returned tuple is the exit code of the
spawned process if equal to or larger than 0. If the subprocess was killed
while running, the exit code will be -1. If the process was stopped because
maxSeconds was exceeded, an exit code equal to -2 will be returned.

If user or group is defined (as name of number), the process will
setuid/setgid to this user and group before executing the command line,
effectively running the child process with the privileges of the provided
user and group.

Remarks:
 * Don't use the '&' shell operator to run a process in the background, use
   the startDaemon function instead
 * Shell operators including pipes and redirects are allowed in the
   command line string
 * When spawning processes which generate large amounts of output, make sure
   you set captureOutput to False, otherwise too much data will be buffered
   in memory
 * If captureOutput is set to False, the values of stdout and stderr in the
   return value will be empty strings
 * If stopOnError is set to True, the calling process will exit with exit
   code 44 if the child process returned a non-zero exit code, or 45 if the
   child process exceeds maxSeconds

@param commandline: Command line string to execute
@type commandline: string
@param showOutput: Bind stdin/stdout/stderr to parent process
@type showOutput: bool
@param captureOutput: Capture generated output
@type captureOutput: bool
@param maxSeconds: Maximum number of seconds the subprocess should be
                   allowed to run
@type maxSeconds: number
@param stopOnError: Quit the caller process when the subprocess fails
@type stopOnError: bool
@param user: Username or UID of user to setuid() to
@type user: string or number
@param group: Groupname of GID of group to setgid() to
@type group: string or number
@param kwargs: Extra arguments passed through to L\{subprocess.Popen\}

@return: Tuple containing subprocess exitcode, stdout and stderr output
@rtype: tuple(number, string, string)

```

#### runDaemon(*commandline, stdout, stderr, user, group, env*) 

```
Run an application as a background process

This function will execute the given commandline decoupled from the host
process by forking first. The stdout and stderr streams of the spawned
application can be redirected to files.

This can be compared to using

    nohup myapplication -u -b 1 &

in a Bash shell.

If no stdout or stderr paths are provided, those streams are ignored.

If user or group is defined (as name of number), the daemon process will
setuid/setgid to this user and group before executing the child process,
effectively running the daemon process with the privileges of the provided
user and group.

If C\{env\} is provided, it will be used as environment in which the daemon
process will be executed. If it is not set, C\{os.environ\} will be used. Do
note C\{PYTHONUNBUFFERED\} and C\{PYTHONPATH\} will be slightly altered (in a
copy of the provided dictionary) by this function before spawning the
daemon process.

@param commandline: Command line string to execute
@type commandline: string
@param stdout: Path to file to redirect stdout
@type stdout: string
@param stderr: Path to file to redirect stderr
@type stderr: string
@param user: Username or UID of user to setuid() to
@type user: string or number
@param group: Groupname of GID of group to setgid() to
@type group: string or number
@param env: Environment settings for the daemon
@type env: dict

@return: PID of the daemonized process
@rtype: number

```

#### runScript(*script, showOutput, captureOutput=True, maxSeconds, stopOnError=True*) 

```
Execute a Python script

This function executes a Python script, making sure the script output will
not be buffered.

For an overview of the parameters and function behavior, see the
documentation of L\{jumpscale.system.process.run\}.

@param script: Script to execute
@type script: string

@return: Tuple containing subprocess exitcode, stdout and stderr output
@rtype: tuple(number, string, string)

@raise ValueError: Script is not an existing file

@see: jumpscale.system.process.run

```

#### setEnvironmentVariable(*varnames, varvalues*) 

```
Set the value of the environment variables C\{varnames\}. Existing variable are overwritten

@param varnames: A list of the names of all the environment variables to set
@type varnames: list<string>
@param varvalues: A list of all values for the environment variables
@type varvalues: list<string>

```

