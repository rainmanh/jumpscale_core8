
# Writing a tool for j.tools

1- Switch to the tools directory:

```cd jumpscale_core8/lib/JumpScale/tools```/

2- Create a package directory:

```mkdir hello```

3- Create the package files:

```touch hello.py __init__.py```

4- Edit hello.py
You have to set an alias for you tool

```python
from JumpScale import j

class HelloTool(object):

    def __init__(self):
        self.__jslocation__ = 'j.tools.hello'

    @staticmethod
    def new(msg='Hello'):
        return Hello(msg)

class Hello(object):

    def __init__(self, msg):
        self.msg=msg

    def upper(self):
        return self.msg.upper()

    def lower(self):
        return self.msg.lower()

    def manytimes(self, n):
        return (self.msg + " ")*n + "!!!"

```
5- You will need j.core.db.flushall()/j.core.db.flushdb() to force it to reread the tools directory

6- Use it
```
In [4]: h=j.tools.hello

In [5]: h=j.tools.hello.new("Konnichwa")

In [6]: h.
h.lower      h.manytimes  h.msg        h.upper      

In [6]: h.upper()
Out[6]: 'KONNICHWA'

In [7]: h.lower()
Out[7]: 'konnichwa'

In [8]: h.msg
Out[8]: 'Konnichwa'

In [9]: h.manytimes(3)
Out[9]: 'Konnichwa Konnichwa Konnichwa !!!'

```