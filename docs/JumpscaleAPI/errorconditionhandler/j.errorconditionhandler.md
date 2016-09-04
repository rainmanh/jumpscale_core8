<!-- toc -->
## j.errorconditionhandler

- /opt/jumpscale8/lib/JumpScale/core/errorhandling/ErrorConditionHandler.py
- Properties
    - exceptions
    - lastAction
    - lastEco
    - inException
    - escalateToRedis
    - haltOnError

### Methods

#### checkErrorIgnore(*eco*) 

#### escalateBugToDeveloper(*errorConditionObject, tb*) 

#### excepthook(*ttype, exceptionObject, tb*) 

```
every fatal error in jumpscale or by python itself will result in an exception
in this function the exception is caught.
This routine will create an errorobject & escalate to the infoserver
@ttype : is the description of the error
@tb : can be a python data object or a Event

```

#### getErrorConditionObject(*ddict, msg='', msgpub='', category='', level=1, type='UNKNOWN', tb, tags=''*) 

```
@data is dict with fields of errorcondition obj
returns only ErrorConditionObject which should be used in jumpscale to define an
    errorcondition (or potential error condition)

```

#### getErrorTraceKIS(*tb*) 

#### getFrames(*tb*) 

#### getLevelName(*level*) 

#### halt(*msg, eco*) 

#### parsePythonExceptionObject(*exceptionObject, tb*) 

```
how to use

try:
    ##do something
except Exception,e:
    eco=j.errorconditionhandler.parsePythonExceptionObject(e)

eco is jumpscale internal format for an error
next step could be to process the error objecect (eco) e.g. by eco.process()

@param exceptionObject is errorobject thrown by python when there is an exception
@param ttype : is the description of the error, can be None
@param tb : can be a python data object for traceback, can be None

@return a ErrorConditionObject object as used by jumpscale (should be the only type of
    object we pass around)

```

#### processPythonExceptionObject(*exceptionObject, tb*) 

```
how to use

try:
    ##do something
except Exception,e:
    j.errorconditionhandler.processexceptionObject(e)

@param exceptionObject is errorobject thrown by python when there is an exception
@param ttype : is the description of the error, can be None
@param tb : can be a python data object for traceback, can be None

@return [ecsource,ecid,ecguid]

the errorcondition is then also processed e.g. send to local logserver and/or stored
    locally in errordb

```

#### raiseWarning(*message, msgpub='', tags='', level=4*) 

```
@param message is the error message which describes the state
@param msgpub is message we want to show to endcustomers (can include a solution)

```

#### reRaiseECO(*eco*) 

#### setExceptHook(**) 

#### toolStripNonAsciFromText(*text*) 

