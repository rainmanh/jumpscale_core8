## AYS Service Unique Keys

Each AYS service instance has a unique key.

This unique key is formatted as `$name!$instance@role ($version)`

You can select one or more service instances by using the full key or just parts of the key:

+ `$name` will select all the services with name = 'name'
+ `!$instance` will select all the services with the instance name = 'instance'
+ `$name!$instance` will select the service with name = 'name' and instance name = 'instance'
+ `@role` will select all the services with the role = 'role'

AYS service instances can be identified using this key format.

For example, in a `jshell`:
```bash
# select the AYS repo in the current directory
repo = j.atyourservice.get()
# select the datacenter service that has the instance name ovh_germany1
datacenter = repo.getServiceFromKey('datacenter!ovh_germany1')
```
