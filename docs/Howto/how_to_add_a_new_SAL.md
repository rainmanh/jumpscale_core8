## How to add a new SAL

### 1. Goto to the SAL directory

```shell
cd jumpscale_core8/lib/JumpScale/sal
```


### 2. Create a package directory

```shell
mkdir hello
```

### 3. Create the package files

```shell
touch Hello.py __init__.py
```

### 4. Edit Hello.py

Each SAL object is required to extend the base SALObject class.

SAL modules must have a name that starts with capital letter to be loaded (for instance `Hello.py` instead of `hello.py`)

```python
from JumpScale import j

class Hello:

    def __init__(self):
        self.__jslocation__ = 'j.sal.hello'
        self.logger = j.logger.get('j.sal.hello')
        self.msg=''
        
    def message(self, msg):
        self.msg = msg
    
    def upper(self):
        return self.msg.upper()

    def lower(self):
        return self.msg.lower()

    def manytimes(self, n):
        return (self.msg + " ")*n + "!!!"
```

### 5. Force a re-read of the SALs directory

In order to force a re-read of the SALs directory you will need to execute:

```python
j.core.db.flushall()/j.core.db.flushdb()
````

### 6. (Re)start the `js` session


## 7. Use the new SAL

```python
In [1]: j.sal.hello.upper()
Out[1]: ''

In [2]: j.sal.hello.message('hello')

In [3]: j.sal.hello.manytimes(3)
Out[3]: 'hello hello hello !!!'
```