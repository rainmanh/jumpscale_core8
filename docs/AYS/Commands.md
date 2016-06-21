## AYS Commands

### overview of commands

```
Usage: ays [OPTIONS] COMMAND [ARGS]...

Options:
  --nodebug  disable debug mode
  --help     Show this message and exit.

Commands:
  commit
  destroy        reset in current ays repo all services &...
  do             call an action
  init           as first step this command will look for...
  install        make it reality if you want more finegrained...
  list
  printlog
  setstate
  showactions    shows all services with relevant actions
  showparents
  showproducers
  simulate
  test           cmds are - doall - push - pull
```

to get more help about 1 command do

```
ays commit --help
```

### the different commands and their purpose

#### ays update

to make sure you are working on most recent data

```
ays update --help
Usage: ays update [OPTIONS]

  update the metdata for the templates as well as the current ays repo

Options:
  -b, --branch TEXT  Name of branch, can be used in pull request to do change
                     mgmt.
  --help             Show this message and exit.
```

#### ays blueprint

- If starting from a blueprint than this command is the first one to run.
- The blueprint will create instances of ays
- Alternative you can also create ays instances with ays init (with or without data option)


```
ays blueprint --help
Usage: ays blueprint [OPTIONS] [PATH]

  will process the blueprint(s) pointed to

  it path is directory then all blueprints in directory will be processed
  (when not starting with _) if is file than only that 1 file

  if path=="" then blueprints found in $aysdir/blueprints will be processed

  if role & instance specified then only the ays instances with specified
  role/instance will be processed

Options:
  -r, --role TEXT      optional role for ays instances to init
  -i, --instance TEXT  optional name of instance
  --help               Show this message and exit.
```

- The process that takes places is:
    - copy template files to appropriate destination (in your ays repo e.g. `/Users/kristofdespiegeleer1/code/jumpscale/ays_core_it/services/sshkey!main`)
    - call actions.input
        - goal is to manipulate the arguments which are the basis of the instance.hrd, this allows the system to avoid questions to be asked during install (because of @ASK statements in the instance.hrd files)
        - in actions.input manipulate the 'args' argument to the method
        - return True if action was ok
        - ask the non configured items from schema.hrd (the @ASK commands, the ones not filled in in previous step
    - call actions.hrd
        - now the @ASK is resolved and the input arguments, this step allows to further manipulate the hrd files
        - examples: create an ssh key and store in hrd file
        - after this action the ays directory is up to date with all required configuration information
        - information outside can be used to get info in hrd e.g. stats info from reality db
    - apply all instance & service.hrd arguments on the action files in the deployed ays instance directory
        - this means that all action files have all template arguments filled in


#### ays init

- the init step will see what needs to be done & detect all change to the system

```
ays init --help

Usage: ays init [OPTIONS]

    step1: 
    ------
    init will look for blueprints 
    (they are in your ays repo under path $aysdir/blueprints)
    they will be processed in sorted order
    the blueprints will be converted to ays instances
    
    step2:
    ------ 
    init will walk over all existing recipes (ays templates in local context)
    and will see if recipe actions or hrd's changed
    if there is change than all ays instance originating from this recipe's state will be changed
    this will allow the further install action to execute on the change

    if there is change in hrd then:
        - change_hrd_template() on the ays instance actions is called
    if there is change in ine if the actions methods then:
        - change_method() on the ays instance actions is called
    This allows action to manipulate the ays tree as result of change

    step3: 
    ------
    init will walk over all existing ays instances
    init will detect if instance.hrd got changed
    if change than the change will be marked in the state file

    if change in hrd then
        - change_hrd_instance() will be called on ays instance actions

    REMARK:
    blueprints are no longer processed in init step, use the ays blueprint command        

Options:
Options:
  -r, --role TEXT      optional role for ays instances to init
  -i, --instance TEXT  optional name of instance
  -d, --data TEXT      data to populate a specific instance
  --help               Show this message and exit.
```

- data can be passed to init to fill in the hrd's (in that case role & instance needs to be specified)
- if not used then questions will be asked to fill in the hrd

```
ays init -r redis -i system --data 'param.name:system param.port:7766 param.disk:0  param.mem:100 param.ip:127.0.0.1 param.unixsocket:0 param.passwd:'

#whatever you pass with --data is used to populate the hrd of the instance

```

#### ays commit

- best practices is to commit the changes back to the git repo
- this will allow change to be recorded & git workflow management can be used to accept the change and let ays install make the change reality.

```
ays commit --help

Usage: ays commit [OPTIONS]

Options:
  -b, --branch TEXT   Name of branch, can be used in pull request to do change
                      mgmt.
  -m, --message TEXT  Message as used in e.g. pull/push.
  -p, --push          if True then will push changes to git repo.
  --help              Show this message and exit.
```


#### ays install

```bash
ays install --help
Usage: ays install [OPTIONS]

  make the ays instances reality (install) if you want more finegrained
  controle please use the do cmd e.g. to start, ...

Options:
  --role TEXT           optional role for ays instances execute an action on
  --instance TEXT       optional name of instance
  --force               if True then will ignore state of service action.
  --producerroles TEXT  roles of producers which will be taken into
                        consideration, if * all
  --ask                 ask on which service to execute the action
  --help                Show this message and exit.
```

#### ays do

```
ays do --help
Usage: ays do [OPTIONS] ACTION

  call an action (which is a method in the action file e.g.
  start/stop/export/...)

Options:
  -r, --role TEXT       optional role for ays instances execute an action on
  -i, --instance TEXT   optional name of instance
  --force               force execution even if no change
  --producerroles TEXT  roles of producers which will be taken into
                        consideration, if * all
  --ask                 ask on which service to execute the action
  --help                Show this message and exit.
```

#### ays simulate

- same as ays do but does not execute, just shows what would be happening.

```
ays simulate [OPTIONS] ACTION

  is like do only does not execute it, is ideal to figure out what would
  happen if you run a certain action

Options:
  --role TEXT           optional role for ays instances execute an action on
  --instance TEXT       optional name of instance
  --force               if True then will ignore state of service action.
  --producerroles TEXT  roles of producers which will be taken into
                        consideration, if * all
  --help                Show this message and exit.
```

#### ays list

```
ays list --help
Usage: ays list [OPTIONS]

Options:
  --role TEXT
  --instance TEXT
  --help           Show this message and exit.
```

#### ays destroy

- the dangerous command, destroys ays instances

```
ays destroy --help
Usage: ays destroy [OPTIONS]

  reset in current ays repo all services & recipe's in current repo
  (DANGEROUS) all instances will be lost !!!

  make sure to do a commit before you do a distroy, this will give you a
  chance to roll back.

Options:
  --help  Show this message and exit.
```

#### ays test

```
ays test --help
Usage: ays test [OPTIONS] CMD

  there is a test suite for ays, this command allows to control the test
  suite

  cmds are  - doall : execute all tests  - push : push modified tests to the
  repo  - pull : get the repo with the tests

Options:
  -n, --name TEXT     Name of test.
  -m, --message TEXT  Message as used in e.g. pull/push.
  --help              Show this message and exit.
```

### less used commands

#### ays showparents

```
ays showparent --help
Usage: ays [OPTIONS] COMMAND [ARGS]...

Error: No such command "showparent".
bash-3.2$ ays showparents --help
Usage: ays showparents [OPTIONS] ROLE INSTANCE

Options:
  --help  Show this message and exit.
```

#### ays showproducers

```
ays showproducers --help
Usage: ays showproducers [OPTIONS] ROLE INSTANCE

Options:
  --help  Show this message and exit.
bash-3.2$ ays showproducers --help
Usage: ays showproducers [OPTIONS] ROLE INSTANCE

  find the producers for this service & show

Options:
  --help  Show this message and exit.
```

#### ays setstate

```
ays setstate --help
Usage: ays setstate [OPTIONS] ACTION

  be careful what you do with this command this sets the state of an ays
  instance manually

Options:
  --state TEXT          state to set
  --role TEXT           optional role for ays instances execute an action on
  --instance TEXT       optional name of instance
  --force               if True then will ignore state of service action.
  --producerroles TEXT  roles of producers which will be taken into
                        consideration, if empty then none
  --help                Show this message and exit.
```