## AYS service.hrd

This is next to `schema.hrd` and the optional `actions.py` the `service.hrd` is another optional metadatafile for a service.

It contains information defining:
- Recurring action methods
- How to react on changes
- How to run processes

It has 4 optional sections, dealing with:
- Processes
- Code recipes
- Recurring methods/actions
- State change management

Below we discuss each of them.


### Process section

This is where you can define processes and how they will run on a local or remote systems.

In the below example we define one process.

```yaml
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

So for each process you have following entries:
- process.<integer-value> defining the process, with an integer for uniquelly identifing the process

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
  
  > Note: If ports are defined it is used to check if the process is started or stopped

- env.process.<integer-value>  sets the environment variables for process indentified with <interger-value>

Processes are started sequentially in the order of the integer value identifying the process.


### Code recipe section

In the code recipe section you provide information about where to fetch code in case it still needs to be build.

In the below example there is also an export directive, defining a website to be setup:

```yaml
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

### Recurring section

In the recurring section you define the actions to be executed on an recurring bases.

Example:

```yaml
recurring.monitor = 1m
recurring.export = 1d
```

Following conditions apply for values used here: 
- Only 3m, 3d and 3h (3 can be any integer value) or just an integer when you mean seconds
- In case of seconds, value should be at least 5


### State change management

In this section you define which actions should be triggered when certain events occur. Below some examples.

A restart is triggered when any change occurs in any HRD or any action is called:
```yaml
actions.state.restart.do = "hrd:* actions.*"
```

A restart is triggered when in the HRD the value of the `service.name` key changes or when the action methods start/stop change
```yaml
actions.state.restart.do = "hrd:service.name actions:start,stop"
```

A reinstallation is triggered when anything changes in the HRD or when the install method changes
```yaml
actions.state.install.do = "hrd:* actions:install"
```

Monitoring will stop when the result of the action method check_mother = 0
```yaml
actions.state.monitor.disabled = "result.check_mother:0 "
```