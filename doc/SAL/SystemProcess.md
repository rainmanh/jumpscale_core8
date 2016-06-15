# SystemProcess
`j.sal.process` helps you to do many tasks/inspection on processes 

## Available helpers
* Execute a command without using a pipe
```
 executeWithoutPipe(self, command, die = True, printCommandToStdout = False)
```
* Execute a command asynchronously 
```  
 executeAsync(self, command, args = [], printCommandToStdout = False, redirectStreams = True, argsInCommand = False, useShell = None, outputToStdout=True):
```
```
* Execute independently `nohup` 
executeIndependant(self,cmd)
```

```
* Executing a python script
executeScript(self, scriptName)
```
@FIXME: executes a command in a sandbox
```
executeInSandbox(self, command, timeout=0)
```
* Executing `code` given that code is a defined function
```
executeCode(self,code,params=None)
```
* Check if a PID is alive.
```
isPidAlive(self, pid)
```
* Get PIDs of a certain process
```
getPidsByFilter(self,filterstr)
```
> Note: It's usually used like this ```j.sal.process.getPidsByFilter("pyth")``` and It'll returns the pids of all process filtered by the word pyth
```
checkstart(self,cmd,filterstr,nrtimes=1,retry=1)
```
```
checkstop(self,cmd,filterstr,retry=1,nrinstances=0)
```
```
getProcessPid(self, process)
```
```
getMyProcessObject(self)
```
```
getProcessObject(self,pid)
```
* Get the PIDss of processes started by `user`
```
getProcessPidsFromUser(self,user)
```
* Kill processes by user
```
killUserProcesses(self,user)
```
```
getSimularProcesses(self)
```
 * Check if a process is running
```
checkProcessRunning(self, process, min=1)
```
```
checkProcessForPid(self, pid, process)
```
* Set environment variables 
```
setEnvironmentVariable(self, varnames, varvalues)
```
* Get the pid of processes using port `port`
```
getPidsByPort(self, port)
```
* Kill a process by its name
```
killProcessByName(self,name,sig=None)
```
* Kill process on port `port`
```
killProcessByPort(self,port)
```
```
getProcessByPort(self, port)
```
* Check if app `appname` is active
```
appCheckActive(self,appname)
```
* Get the number of instances of app `appname`
```
appNrInstances(self,appname)
```
* Get the number of active instances of app `appname`
```
appNrInstancesActive(self,appname)
```
* Get the environment of `pid`
```
getEnviron(self, pid)
```
* Get all of the `pids` of app `appname`
```
appGetPids(self,appname)
```
```
appsGetNames(self)
```
* Get a list of all defunct processes
```
getDefunctProcesses(self)
```
```
appsGet(self)
```
* Get all active PIDs of app `appname`
```
appGetPidsActive(self,appname)
```


