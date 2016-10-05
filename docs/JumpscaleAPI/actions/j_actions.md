<!-- toc -->
## j.actions

- /opt/jumpscale8/lib/JumpScale/tools/actions/ActionController.py
- Properties
    - last
    - lastOnes
    - logger
    - rememberDone

### Methods

Manager controlling actions

#### add(*action, actionRecover, args, kwargs, die=True, stdOutput, errorOutput=True, retry, serviceObj, deps, executeNow=True, selfGeneratorCode='', force=True, showout, actionshow=True, dynamicArguments*) 

```
self.doc is in doc string of method
specify recover actions in the description

name is name of method

@param name if you want to overrule the name

@param id is unique id which allows finding back of action
@param loglevel: Message level
@param action: python function to execute
@param actionRecover: link to other action (same as this object but will be used to
    recover the situation)
@param args is dict with arguments
@param serviceObj: service, will be used to get category filled in e.g.
    selfGeneratorCode='selfobj=None'
    needs to be done selfobj=....  ... is whatever code which fill filling selfobj
    BE VERY CAREFUL TO USE THIS, DO NEVER USE IN GEVENT OR ANY OTHER ASYNC FRAMEWORK

@param dynamicArguments are arguments which will be executed before calling the method
    e.g.
   dargs=\{\}
   dargs["service"]="j.atyourservice.getService("%s")"%kwargs["service"]

```

#### addToStack(*action*) 

#### delFromStack(*action*) 

#### get(*actionkey*) 

#### gettodo() 

#### reset(*all, runid, prefix*) 

```
@param is the key under actions we need to remove

```

#### resetAll() 

#### run(*agentcontroller*) 

#### selectAction() 

#### setRunId(*runid, reset*) 

#### setState(*state='INIT'*) 

