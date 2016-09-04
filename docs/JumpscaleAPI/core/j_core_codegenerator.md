<!-- toc -->
## j.core.codegenerator

- /opt/jumpscale8/lib/JumpScale/core/codegentools/CodeGenerator.py
- Properties
    - generated
    - classes
    - appdir
    - codepath

### Methods

#### generate(*spec, type, typecheck=True, dieInGenCode=True, appserverclient, instance, redis, wsclient, codepath, classpath, returnClass=True, args, makeCopy*) 

```
param: spec is spec we want to generate from
param: type JSModel,actormethodgreenlet,enumeration,actorlocal
param: typecheck (means in generated code the types will be checked)
param: dieInGenCode  if true means in generated code we will die when something
    uneforeseen happens
return: dict of classes if more than 1 otherwise just the class

```

#### getClassEnumeration(*appname, actor, enumname, typecheck=True, dieInGenCode=True*) 

#### getClassJSModel(*appname, actor, modelname, typecheck=True, dieInGenCode=True, codepath=''*) 

#### getClassactorLocal(*appname, actor, typecheck=True, dieInGenCode=True*) 

#### getClassesactorMethodGreenlet(*appname, actor, typecheck=True, dieInGenCode=True*) 

```
return: returns dict with key name methodname and then the class (for each method a class
    is generated)

```

#### getCodeEveModel(*appname, actor, modelname, typecheck=True, dieInGenCode=True, codepath=''*) 

#### getCodeId(*spec, type*) 

#### getCodeJSModel(*appname, actor, modelname, typecheck=True, dieInGenCode=True, codepath=''*) 

#### getactorClass(*appname, actor, typecheck=True, dieInGenCode=True, codepath*) 

#### removeFromMem(*appname, actor*) 

#### resetMemNonSystem() 

#### setTarget(*target*) 

```
Sets the target to generate for server or client

```

