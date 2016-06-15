## Human Readable Data

### About HRD

* HRD is the configuration format in jumpscale.
* Used in AtYourService configuration.
* HRD is a more easily read and interpreted format for data, that is friendly to system engineers too.
* Can even be used as a template engine!
* It can be used to represent:
 * Configuration files
 * Database objects

* * * * *

### Example Of An HRD File

```shell

#!text
bootstrap.ip=localhost
bootstrap.login=root
bootstrap.passwd=rooter
bootstrap.type=ssh
```

* * * * *

### HRD Schema

defines the structure of an HRD
the schema can produce an HRD

example
```
email = descr:'comma separated list of email addresses' type:email alias:'mail,mailaddr' @ask list
mobile = descr:'comma separate list of mobile phone nrs' type:tel alias:'tel,landline' @ask list
expire = descr:'format $day:$month:$year' type:date alias:till @ask
test = type:int default:1
testf = type:float default:1.1
testb = type:bool default:False
```

properties
- descr
    - describes the field
- type 
    - str,email,int,float,bool,multiline,tel,ipaddr,date
    - date = epoch (int)
- default
    - default value for this type
- regex
    - if you want to validate the entry against a regex
- minval/maxval
    - only relevant for int, what is min value for int & max
- multichoice
    - list of items people can select from e.g. ```'red,blue,orange'```
- singlechoice
    - like multichoice but can only select 1
- alias
    - alias for this property, can be list
- @ask
    - is a tag, if mentioned means we will ask for the value when not provided, if this is not mentioned then the default value will be used 
- list
    - tells the schema that the type is a list
    - e.g. can be a list of ints, of strings, ...
- id
    - is tag
    - identifies which field is the id
    - if not specified name = $(instance) will be autoadded
- consume
    - format ```$role:$minamount:$maxamount,$role2:$min$max, ...```
    - $minamount-$maxamount is optional
    - $role is role of other atyourservice e.g. node (consume service from a node)
    - example: ```node:1:1,redis:1:3```
    - the min-max are important because they define the dependency requirements e.g. node:1:1 means I need 1 node to be in good shape and if node is not there I cannot function myself.
- parent
    - specifies a role
    - $role is role of other atyourservice e.g. node (consume service from a node)
    - it acts like a consume ```$role:1:1``` but has special meaning
    - when parent then the service instance will be subdir of parent in ays repo
- parentauto
    - is tag to parent
    - means will automatically create the parent if it does not exist yet 

consume example
```python
node = type:str list descr:'node on which we are installed' consume:node:1:1
etcd = type:str list consume:etcd:3:3
mongodb = type:str list consume:mongodb:1:3
nameserver = type:str list consume:ns
```

### get HRD from HRDSchema

```
@todo 
```

### Usage As Template Engine

**Getting application instance HRD's**

```python
@todo needs to be reworked
hrd=j.application.getAppInstanceHRD(name, instance, domain='jumpscale')
#then e.g. use
j.application.config.applyOnDir
j.application.config.applyOnFile
```

**Getting system wide HRD's**

they are all mapped under j.application.config
you can e.g. use following 2 functions to apply your templates to dirs or files

```shell
@todo needs to be reworked
j.application.config.applyOnDir
j.application.config.applyOnFile
```
to look at the HRD just go in ipshell & print the config

The templating function will look for template params \$(hrdkey) and replace them

you can replace additional arguments e.g:

```python
j.application.config.applyOnDir(adir,additionalArgs={"whoami","kds"})
```

would replace \$(whoami) with kds additional to what found in hrd's
