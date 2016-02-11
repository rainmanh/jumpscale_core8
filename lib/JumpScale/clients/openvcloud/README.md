# OpenvCloud

How to create a machine.
To create a machine we need to get the correct size and image to create a machine.

```python
client = j.clients.openvcloud.get('www.mothership1.com', 'demo', 'demo')
image = client.findImage('Ubuntu 15.04')
size = client.findSize(512)
cloudspaces = client.api.cloudapi.cloudspaces.list()
# lets deploy in our first cloud space
machineId = client.api.cloudapi.machines.create(name='My VM',
                                    description='My VM description',
                                    sizeId=size['id'],
                                    imageId=image['id'],
                                    disksize=20,
                                    cloudspaceId=cloudspaces[0]['id'])

machineobject = client.api.cloudapi.machines.get(machineId=machineId)

# get ssh connection
executor = client.getSSHConnection(machineId)

```
