
## easy client

### init

- the current j.ac.get goes to j.ac.getAdvanced(...)

- j.ac.get(... gets new client)

### execution of cmds, jumpscripts

#### get client
```python
cl=j.ac.get()
```

#### basic execution of remote commands (like our j.do.execute ...)

```python
rc,stdout,stderror=cl.execute(cmd,path=None,gid=None,nid=None,roles=[],die=True,timeout=5,data="")
```
* cmd is e.g. 'ls /' no separate args
* path is where to execute the cmd 
* data send to jumpscript over stdin (data can be anything !!!,text, binary, ...)
* if nid specified then roles not used, roles=[] means we ignore it and then we execute over gid & nid
    * gid==None: means all gids
    * nid==None: means all nids

>Q: Does this mean when roles is given (nid=None) we should fanout by default (to all agents that satisfies the set of given roles). I think we need to add a specific `fanout` flag in case roles is given so we either run
on all `nids` or execute on 1 agent that satisfies the roles

* die is std True
* timeout is std 5 sec, if timeout raise an error
* if more than 1 agent involved, then output is concatenation per agent of
    
how to do output when more than 1 agent involved

```bash
$agent ($gid,$nid)
$stdout
##RC:
##ERROR: 
#######################################################

$agent ($gid,$nid)
$stdout
#######################################################

$agent ($gid,$nid)
$stdout
#######################################################
...

```

> Q: Why this weird not machine friendly format, why not return a list of tubles instead liek [(rc, stdout, stderr), ...]

- only show ##ERROR if there was an error
- only show ##RC if RC>0

#### execute a bash script

```python
rc,stdout,stderror=cl.executeBash(cmds,gid=None,nid=None,roles=[],die=True,timeout=5)
```
* cmds is content (string) to execute in bash format
* remark: no data to std in support here, believe not required & wanted for bash scripts
* output see execute cmd above

#### execute a jumpscript

format of a jumpscript is

```python
def action(arg1="",arg2=""):
    # do stuff with the data
    j.logger.log('Received arg is: %s' % arg1)
    result = arg2 + 1
    return result
```
- remark: no need to specify ```from JumpScale import j``` this gets added automatically

how to use

```python
result=cl.executeJumpscript(domain="",name="",content="",path="",method=None,\
    gid=None,nid=None,roles=[],die=True,timeout=5,data="",args={})
```

there are 4 ways to execute a jumpscript

1. use name jumpscript from jumpscript directory (domain,name args need to be used)
2. use content is jumpscript code in format as specified above
3. use path, content will be loaded from the path
4. use method, this is name from python method, source code will be introspected and used as content (see previous)

remarks

* domain & name does not have to be specified 
    * if specified then jumpscript needs to be in right location see [Jumpscripts.md](Jumpscripts.md)
    * @TODO format needs to be different for a jumpscript then specified in Jumpscripts.md
* if no domain/name path or content need to be specified, content get's prio otherwise read from path
    * implementation remark: make sure from jumpscale import get's removed (otherwise double, because i gets reinserted)
* data send to jumpscript over stdin (data can be anything !!!,text, binary, ...)

> Do we really need to send data over stdin to the script? This can be implemented but I really don't see a use case
since you can send anything (including binary) using the `args`.

* args is what will be send to the action(**args) 
* if nid specified then roles not used, roles=[] means we ignore it and then we execute over gid & nid
    * gid==None: means all gids
    * nid==None: means all nids
* result is return of script
    * impl detail: will have to prepend script with jumpscale import & postpend to print the result in right format to our logging mechanism can pick it up
* timeout is in seconds, if it takes longer then error with clean eco as result ! (jumpscale eco obj)

example to use with method

```python
def printMyName(myname=""):
    print "myname:%s"%myname
    return myname
    
results=cl.executeJumpscript(method= printMyName,roles=["*"],die=True,timeout=5,data="",args={"myname":"itsme"})
for result in results:
    print result

```

- remark when executing multiple its better to use the async method see below

implementation remarks

- error in jumpscript (ECO)
    - new errorhandler is created who dumps the output as json & gets captured (log level 8 or 9)
    - this info can get back serialzed as eco & returned to job.error in case there was error
- jumpscripts should be send without syncthing & and only unique content send (use hashing) see https://github.com/Jumpscale/AgentController8/issues/6

#### async execution of a jumpscript

all above cmds are always executed synchronously, so we wait till timeout !!!
the method below is better for execution of many tasks over many agents

```python
jobs=cl.executeJumpscriptAsync(domain="",name="",content="",path="",method=None,\
    gid=None,nid=None,roles=[],die=True,timeout=5,data="",args={})

for job in jobs:

    #job is a nice python object with relevant info about job
    job.check() #will ask agent2 about status and fill in job.status, job.mem, job.cpu
    #for mem & cpu, should be avg over e.g. last 5 min (does agent support that?, if not give last)
    job.status  = done,running,warning or error
    job.mem=
    job.cpu= #is in percentage of total
    job.id = unique id to job
    job.result= #will be none if job still running

    #loglevels see LogLevels page
    logitems=job.getLogs(levels="1-5")
    logitems=job.getLogs(levels="*")
    logitems=job.getLogs(levels="1,2,3")

    job.wait(timeout=5) #wait till job done

    if job.state=="error":
        print job.error  #error is a full error object from jumpscale (ECO)
        ...

    if job.state=="warning":
        print job.warning  #warning is a full error object from jumpscale (ECO)
        ...
```


### agent & process info

```
cl=j.ac.get()
agents=cl.getAgents()
for agent in agents:
    print agent.gid
    print agent.nid
    print agent.hostname
    print agent.macaddr #do as property so we fetch the info when required (all macaddr in list)
    print agent.ipaddr  #do as property so we fetch the info when required (all ip in list)
    print agent.watchdog #time in seconds since last time we saw agent
    print agent.status is : ok, error, unreachable
    print agent.cpu (is cpu aggregated for all processes running underneath agent and agent itself)
    print agent.mem (is mem aggregated for all processes running underneath agent and agent itself)

    for process in agent.processes:
        print process.name
        print process.path ???
        print process.mem ???
        print process.cpu ???
        ...

    #make sure when properties are used that if agent is error or unreachable right errorcondition is thrown (j.events....)



```

### sync

```
cl=j.ac.get()
share=cl.sync_createshare(gid,nid,path,ignore=[])
#ignore is list of items not to sync
print share.path
print share.gid
print share.nid
print share ... #see what else is relevant

share=cl.sync.getshare(gid,nid,path) #gets existing info
print share.peers (see who is connected with their status !!!, need to know if this share is fully synced !!!)
#info is fetched from the syncthing running on that location
print share.insync (means all peerst have the same data for this share !!!)

share.attach(git,nid,path,readonly=False)
#readonly means that destinations will not be able to modify


```

example with master to 2 agents remote

```
cl=j.ac.get()
#1-1 is master
share_downloads=cl.sync_createshare(1,1,"/opt/downloads",ignore=["*.pyc","*.bak","*/.git/*"])
share_downloads.attach(1,2,"/opt/downloads",readonly=True)
share_downloads.attach(1,3,"/opt/downloads",readonly=True)

```

some of the syncthing agents will have to expose their port to internet, otherwise this will not work, this is not job of this interface


### portforward

```
cl=j.ac.get()
cl.tunnel_create(...)
#make sure you check if agents relevant are accesible and if not tell

```
