## AYS Service Unique Keys

Each AYS service instance has a unique key.

This unique key is formatted as `$domain|$name!$instance@role ($version)`

You can select one or more service instances by using the full key and just parts of the key:

+ $domain|$name!$instance
+ $name
+ !$instance
+ $name!$instance
+ @role

AYS service instances can be identified using this key format, below some examples.

- Start (if not started yet) 1 service instance with role MongoDB, if more than 1 then this will fail:

```shell
ays start -n @mongodb
```

- Get the status of all service instances with role node:

```shell
ays status -n @node
```

- Get the status of a service instance which has instance name "ovh4", if more than 1 instance is found then there will be an error:

```shell
ays status -n !ovh4
```