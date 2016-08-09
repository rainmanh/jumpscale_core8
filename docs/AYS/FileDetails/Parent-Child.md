# AYS Parent/Child Relationship

A service can be a parent for other services.

It's just a way of organizing your services and grouping them.

Child services are created in a subdirectory of its parent.

## Example:

Considering the following blueprint:

```yaml
datacenter__eu:
    location: 'Europe'
    description: 'Main datacenter in Europe'

datacenter__us:
    location: 'USA'
    description: 'Main datacenter in USA'


rack__storage1:
    datacenter: 'eu'
    location: 'room1'
    description: 'rack for storage node'

rack__storage2:
    datacenter: 'eu'
    location: 'room1'
    description: 'rack for storage node'

rack__cpu1:
    datacenter: 'us'
    location: 'east building'
    description: 'rack for cpu node'

rack__storage4:
    datacenter: 'us'
    location: 'west buuilding'
    description: 'rack for cpu node'
```

In this example the `rack` service use the datacenter service as parent.<br>
After execution of the command `ays blueprint`, the service tree will look like that:

```shell
$ tree services/
services/
├── datacenter!eu
│   ├── instance.hrd
│   ├── rack!storage1
│   │   ├── instance.hrd
│   │   └── state.yaml
│   ├── rack!storage2
│   │   ├── instance.hrd
│   │   └── state.yaml
│   └── state.yaml
└── datacenter!us
    ├── instance.hrd
    ├── rack!cpu1
    │   ├── instance.hrd
    │   └── state.yaml
    ├── rack!storage4
    │   ├── instance.hrd
    │   └── state.yaml
    └── state.yaml

6 directories, 12 files
```
