# SystemProcess

`j.sal.process` helps you to do many tasks/inspection on processes.

## Available helpers

- Execute a command without using a pipe

```python
 executeWithoutPipe(self, command, die = True, printCommandToStdout = False)
```

- Execute a command asynchronously

```python
 executeAsync(self, command, args = [], printCommandToStdout = False, redirectStreams = True, argsInCommand = False, useShell = None, outputToStdout=True):
```

- Execute independently `nohup`

```python
 executeIndependant(self,cmd)
```

- Executing a Python script

```python
  executeScript(self, scriptName)
```

- @FIXME: execute a command in a sandbox

```python
executeInSandbox(self, command, timeout=0)
```

- Executing `code` given that code is a defined function

```python
executeCode(self, code, params=None)
```

- Check if a PID is alive

```python
isPidAlive(self, pid)
```

- Get PIDs of a certain process

```python
getPidsByFilter(self,filterstr)
```

> Note: It's usually used like this `j.sal.process.getPidsByFilter("pyth")` and It will return the PIDs of all processed filtered by the word pyth

```python
checkstart(self,cmd,filterstr,nrtimes=1,retry=1)
```

```python
checkstop(self,cmd,filterstr,retry=1,nrinstances=0)
```

```python
getProcessPid(self, process)
```

```python
getMyProcessObject(self)
```

```python
getProcessObject(self,pid)
```

- Get the PIDss of processes started by `user`

```python
getProcessPidsFromUser(self,user)
```

- Kill processes by user

```python
killUserProcesses(self,user)
```

```python
getSimularProcesses(self)
```

- Check if a process is running

```python
checkProcessRunning(self, process, min=1)
```

```python
checkProcessForPid(self, pid, process)
```

- Set environment variables

```python
setEnvironmentVariable(self, varnames, varvalues)
```

- Get the pid of processes using port `port`

```python
getPidsByPort(self, port)
```

- Kill a process by its name

```python
killProcessByName(self,name,sig=None)
```

- Kill process on port `port`

```python
killProcessByPort(self,port)
```

```python
getProcessByPort(self, port)
```

- Check if an app `appname` is active

```python
appCheckActive(self,appname)
```

- Get the number of instances of app `appname`

```python
appNrInstances(self,appname)
```

- Get the number of active instances of app `appname`

```python
appNrInstancesActive(self,appname)
```

- Get the environment of `pid`

```python
getEnviron(self, pid)
```

- Get all of the `pids` of app `appname`

```python
appGetPids(self,appname)
```

```python
appsGetNames(self)
```

- Get a list of all defunct processes

```python
getDefunctProcesses(self)
```

```python
appsGet(self)
```

- Get all active PIDs of app `appname`

```python
appGetPidsActive(self,appname)
```
