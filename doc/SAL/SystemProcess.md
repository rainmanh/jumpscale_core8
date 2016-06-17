## SystemProcess

`j.sal.process` helps you to do many tasks/inspection on processes.


### Available helpers

* Execute a command without using a pipe

```py
 executeWithoutPipe(self, command, die = True, printCommandToStdout = False)
```

* Execute a command asynchronously 

```py
 executeAsync(self, command, args = [], printCommandToStdout = False, redirectStreams = True, argsInCommand = False, useShell = None, outputToStdout=True):
```

* Execute independently `nohup` 

```py
 executeIndependant(self,cmd)
```

* Executing a Python script

```py
  executeScript(self, scriptName)
```

* @FIXME: execute a command in a sandbox

```py
executeInSandbox(self, command, timeout=0)
```

* Executing `code` given that code is a defined function

```py
executeCode(self, code, params=None)
```

* Check if a PID is alive

```py
isPidAlive(self, pid)
```

* Get PIDs of a certain process

```py
getPidsByFilter(self,filterstr)
```

> Note: It's usually used like this ```j.sal.process.getPidsByFilter("pyth")``` and It will return the PIDs of all processed filtered by the word pyth

```py
checkstart(self,cmd,filterstr,nrtimes=1,retry=1)
```

```py
checkstop(self,cmd,filterstr,retry=1,nrinstances=0)
```

```py
getProcessPid(self, process)
```

```py
getMyProcessObject(self)
```

```py
getProcessObject(self,pid)
```

* Get the PIDss of processes started by `user`

```py
getProcessPidsFromUser(self,user)
```

* Kill processes by user

```py
killUserProcesses(self,user)
```

```py
getSimularProcesses(self)
```

 * Check if a process is running

```py
checkProcessRunning(self, process, min=1)
```

```py
checkProcessForPid(self, pid, process)
```

* Set environment variables 

```py
setEnvironmentVariable(self, varnames, varvalues)
```

* Get the pid of processes using port `port`

```py
getPidsByPort(self, port)
```

* Kill a process by its name

```py
killProcessByName(self,name,sig=None)
```

* Kill process on port `port`

```py
killProcessByPort(self,port)
```

```py
getProcessByPort(self, port)
```

* Check if an app `appname` is active

```py
appCheckActive(self,appname)
```

* Get the number of instances of app `appname`

```py
appNrInstances(self,appname)
```

* Get the number of active instances of app `appname`

```py
appNrInstancesActive(self,appname)
```

* Get the environment of `pid`

```py
getEnviron(self, pid)
```

* Get all of the `pids` of app `appname`

```py
appGetPids(self,appname)
```

```py
appsGetNames(self)
```

* Get a list of all defunct processes

```py
getDefunctProcesses(self)
```

```py
appsGet(self)
```

* Get all active PIDs of app `appname`

```py
appGetPidsActive(self,appname)
```