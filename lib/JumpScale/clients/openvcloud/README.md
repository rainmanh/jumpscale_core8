# OpenvCloud

How to create a machine.
To create a machine we need to get the correct size and image to create a machine.

```python
client = j.clients.openvcloud.get('www.mothership1.com', 'demo', 'demo')
account = client.account_get('demo')
locations = client.locations
location = locations[0]['locationCode']

space = account.space_get('demospace', location=location)

# lets deploy in our first cloud space
machine = space.machine_create(name='My VM',
                                image='Ubuntu 15.10 x64',
                                memsize=512)

executor = machine.get_ssh_connection()

```
