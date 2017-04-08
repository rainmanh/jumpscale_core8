<!-- toc -->
## j.data.idgenerator

- /opt/jumpscale8/lib/JumpScale/data/idgenerator/IDGenerator.py

### Methods

generic provider of id's
lives at j.data.idgenerator

#### generateCapnpID() 

```
Generates a valid id for a capnp schema.

```

#### generateGUID() 

```
generate unique guid
how to use:  j.data.idgenerator.generateGUID()

```

#### generateIncrID(*incrTypeId, service, reset*) 

```
type is like agent, job, jobstep
needs to be a unique type, can only work if application service is known
how to use:  j.data.idgenerator.generateIncrID("agent")
@reset if True means restart from 1

```

#### generateRandomInt(*fromInt, toInt*) 

```
how to use:  j.data.idgenerator.generateRandomInt(0,10)

```

#### generateXCharID(*x*) 

#### getID(*incrTypeId, objectUniqueSeedInfo, service, reset*) 

```
get a unique id for an object uniquely identified
remembers previously given id's

```


```
!!!
title = "J.data.idgenerator"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.data.idgenerator"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.data.idgenerator"
date = "2017-04-08"
tags = []
```
