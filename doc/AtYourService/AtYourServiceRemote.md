### AtYourService remote execution (OUTDATED)

AtYourService allows you to create and manage a full environment.
In order to be able to contact the remote machines, you need to write the services that will handle these communications.

To have an idea of what can be created, lets have a look at a concrete example.

Example of a remote node installation

**Through a script**
```python
from JumpScale import j

# creation of a node

data = {
    'jumpscale.install': False,
    'jumpscale.update': False
    'node.tcp.addr': "localhost"
}

node = j.atyourservice.new(name='node.local', args=data)
node.init()

# Service should be created with the node as a parent, indicating it
# should be installed on the previously defined node

allinone = j.atyourservice.new(name='singlenode_portal', args=data, parent=node)
allinone.init()

# Apply the changes prepared

j.atyourservice.apply()
```

Have a look at the services template used in this example :
- [node.local](https://github.com/Jumpscale/ays_jumpscale8/tree/ays_unstable/_ays/node.local)
- [singlenode_portal](https://github.com/Jumpscale/ays_jumpscale8/tree/ays_unstable/_jumpscale/singlenode_portal)
