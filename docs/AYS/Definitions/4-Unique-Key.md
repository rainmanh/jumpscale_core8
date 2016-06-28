## AYS Service Unique Keys

Each AYS service instance has a unique key.

This unique key is formatted as `$domain|$name!$instance@role ($version)`

You can select one or more service instances by using the full key and just parts of the key:

+ $domain|$name!$instance
+ $name
+ !$instance
+ $name!$instance
+ @role

AYS service instances can be identified using this key format.

For example, in a `jsshell`:
```bash
repo = j.atyourservice.get('fake_IT_env')
repo.getServiceFromKey('datacenter!ovh_germany1')
```