# Using the Interactive Shell & Debugging

## js

In order to start the JumpScale shell just type 'js'.

There are many more command line tools installed for you to explore, type 'js' and hit the tab key and you will see...

```python
# js
IPython ? -- An enhanced Interactive Python.
?         -> Introduction and overview of IPython's features.
%quickref -> Quick reference.
help      -> Python's own help system.
object?   -> Details about 'object', use 'object??' for extra details.

In [1]:
```

## Import JumpScale in any Python script

e.g. try using ipython.

```python
from JumpScale import j
j.[tab]
```

Now underneath j there is a basic set of functionality available. Just type j and then hit the tab key.

There are tons of extensions available which can be installed using jspackages (more about that later).

## From an existing Python script start JumpScale and go to the debug shell

```python
from JumpScale import j

#your python code here ... optionally using jumpscale

from IPython import embed
print "DEBUG NOW in my shell on pos X"
embed()
```

Your script will now stop and show you an ipython console in which you can inspect your code and work with all variables in an interactive way.

## Alternative way of debugging ipdb

Install ipdb `apt-get install python-ipdb` or `pip install ipdb`

ipdb exports functions to access the IPython debugger, which features tab completion, syntax highlighting, better tracebacks, better introspection with the same interface as the pdb module.

```python
print "Debug point for checking ...."
import ipdb; ipdb.set_trace()

 ipdb.set_trace()
--Call--
> /usr/lib/python2.7/dist-packages/IPython/core/displayhook.py(228)__call__()
    227 
--> 228     def __call__(self, result=None):
    229         """Printing with history cache management.

ipdb> help

Documented commands (type help <topic>):
========================================
EOF    bt         cont      enable  jump  pdef   r        tbreak   w     
a      c          continue  exit    l     pdoc   restart  u        whatis
alias  cl         d         h       list  pinfo  return   unalias  where 
args   clear      debug     help    n     pp     run      unt    
b      commands   disable   ignore  next  q      s        until  
break  condition  down      j       p     quit   step     up     

Miscellaneous help topics:
==========================
exec  pdb

Undocumented commands:
======================
retval  rv
```

More info about ipdb \<<https://github.com/gotcha/ipdb>>

```
!!!
title = "How To Use The Shell And Debug"
date = "2017-04-08"
tags = ["howto"]
```
