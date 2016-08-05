## AYS Service Unique Keys

Each AYS service instance has a unique key.

This unique key is formatted as `$name!$instance@role ($version)`

You can select one or more service instances by using the full key and just parts of the key:

+ `$name` : will select all the service with name = 'name'
+ `!$instance` : will select all the service with the instance name = 'instance'
+ `$name!$instance` : will select the service with name = 'name' and instance name = 'instance'
+ `@role` : will select all the service with the role = 'role'

AYS service instances can be identified using this key format.

For example, in a `jsshell`:
```bash
# select the AYS repo in the current directory
repo = j.atyourservice.get()
# select the datacenter service that has the instance name ovh_germany1
datacenter = repo.getServiceFromKey('datacenter!ovh_germany1')
```
