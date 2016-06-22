## AYS Files

### AYS Template Repo

- Template repos contain all the metadata defining the life cycle of a service, from pre-installation to monitoring
- An example is [ays_jumpscale8](https://github.com/Jumpscale/ays_jumpscale8), defining the full life cycle of the AYS JumpScale services
- You can configure which AYS Tempalte repos to use in a config file:
    - Edit the file ```/optvar/hrd/system/atyourservice.hrd```
    - Add new section for every metadata repo you want to add
    
    ```shell
    #here domain=jumpscale, change name for other domains
    metadata.jumpscale             =
        branch:'master',
        url:'https://github.com/Jumpscale/ays_jumpscale8',

    metadata.openvcloud        =
        url:'https://git.aydo.com/0-complexity/openvcloud_ays',
    ```

- AtYourService uses [git](http://git-scm.com) to manage its metadata
    - All metadata repos are cloned as subdirs of ```/opt/code/$type/```
        - Repos from github are cloned into ```/opt/code/github```
        - Repos from other git repos are cloned into ```/opt/code/git/```
        - So ```https://github.com/Jumpscale/ays_jumpscale8``` is cloned into ```/opt/code/github/jumpscale/ays_jumpscale8```
- Each AYS template defines these files:
    * **service.hrd** 
      * has information for recurring action methods
      * has information for state changes (how to react on changes)
      * has information about how to run processes
    * **schema.hrd** 
      * is schema for the metadata file relevant for an instance of a service
      * has information about how services interact with each other through:
          - Parentage
          - Consumption
          - Read more about these relationships in [AYS Basics](2_AYS_basics.html) in sections addressing *Producers & Consumers* and *Parents*
      * has parameter definitions used to configure a service
      * for example:
          ```
            image = type:str default:'ubuntu'
            build = type:bool default:False
            build.url = type:str
            build.path = type:str default:''
            ports = type:str list

            sshkey = descr:'authorized sshkey' consume:sshkey:1:1 auto

            os = type:str parent:'os'
            docker = type:str consume:'app_docker':1 auto
            docker.local = type:bool default:False
          ```
    * **actions.py** 
      * defines the behavior of this service's actions.

### AYS Repo

- this is the main repo from which services are deployed, executed, ...
- git repo in which we describes a full deployment of any amount of services
- the ays repo is build starting from some blueprint files
- a blueprint is a high level description of what needs to be be instantianated
- 4 directories are relevant in such a ays repo
    - blueprints
        - high level files that define what needs to be done
    - servicetemplates
        - local set of ays templates
        - if ays looks for a template starting from an ays repo, it will always look first in this directory if template found, if not then it will get it from the ays metadata template repo
    - recipes
        - local copy of the ays template
        - made ready for consumption in relation to local ays repo  
        - has no further meaning than being a local copy, this is done to be able to see changes in the template on local repo level (git)
    - services
        - the expanded services
        - an instance.hrd file has al the info as required to make a deployment reality 
        - an state.md file which is the file which has all info to do with states & results of executing actions

### AYS service.hrd

#### service.hrd Process Section

this is how you can define processes & how they will be run on a local or remote system

```python
process.1=
    cmd:'/opt/mongodb/bin/mongod',
    args:'--dbpath $(system.paths.var)/mongodb/$(service.instance)/ --smallfiles --rest --httpinterface',
    prio:5,
    cwd:'/opt/mongodb/bin',
    timeout_start:60,
    timeout_stop:10,
    ports:27017;28017,
    startupmanager:tmux,
    filterstr:'bin/mongod'

env.procces.1 =
    LC_ALL:C,
```

##### process.1

The number `1` here is the order of the process if multiple processes are defined they have to have a unique order.

| Key | Type | Description |
|-----|------|-------------|
|cmd  | string| Commands to execute |
|args | string | Arguments to command |
|prio | int | Priority when all process are started from low to high |
|cwd  | string | Current working directory for the process |
|timeout_start| int | Timeout in seconds to mark the process as failed if not running yet |
|timeout_stop| int | Timeout in seconds to forcekill process if not stopped yet |
|ports| list of int| Semi column seperate list of tcp ports the process should listen on |
|startupmanager| sting | Tmux|
|filterstr| string| grep like string to identify the started process |

* Note: If ports is defined it is used to check if the process is started or stopped

##### env.process.1

Environment variables for process `1`


#### service.hrd code.recipe section


this info is used during building


```python
git.build.1=
    site:'git.aydo.com',
    account:'static-websites',
    repo:'new-gig',

git.export.1                   =
    dest:'$(system.paths.base)/apps/www/gig',
    link:'True',
    source:'www.greenitglobe.com',
    site:'git.aydo.com',
    account:'static-websites',
    repo:'new-gig',
```

- if ssh-agent is loaded & a key has been found then the checkout will happen over ssh.
    - we strongly recommend this way of working
- if not http will be used

#### service.hrd recurring section

```python
recurring.monitor = 1m
recurring.export = 1d
```

the period e.g. 1m format

- only supported now is 3m, 3d and 3h (ofcourse 3 can be any int) and an int which are seconds
- needs to be at least 5 seconds


#### state change management

```python
#any change on hrd or actions will trigger a restart
actions.state.restart.do = "hrd:* actions.*"

#when hrd with key service.name changes or action methods start/stop change then restart
actions.state.restart.do = "hrd:service.name actions:start,stop "

#when hrd or install method on actions and actions_node changes then redo the install
actions.state.install.do = "hrd:* actions:install actions_node:install"

#stop monitoring when the result of action method check_mother == 0
actions.state.monitor.disabled = "result.check_mother:0 "

```