AYS Parent/Child relationship
-------------------------------

A service can be a parent for other services. It's a way of organizing your services and grouping them.

Child services are created under the directory of the parent.


### To create a nested child service:
@todo 

```
# Create a parent node
ays init -n node.local -i test --data 'jumpscale.install:False jumpscale.update:False'

# Init a service that has the node as its parent:
ays init -n test --parent '!test@node'

# Apply these changes
ays apply


# File structure will look like this:
-- node!test
    |-- actions.py
    |-- instance.hrd
    |-- instance_old.hrd
    |-- rolename!test
    |   |-- actions.py
    |   |-- instance.hrd
    |   |-- instance_old.hrd
    |   |-- state.hrd
    |   `-- template.hrd
    |-- state.hrd
    |-- template.hrd
    |-- test4!test
    |   |-- actions.py
    |   |-- instance.hrd
    |   |-- instance_old.hrd
    |   |-- state.hrd
    |   `-- template.hrd
    |-- test5!test
    |   |-- actions.py
    |   |-- instance.hrd
    |   |-- instance_old.hrd
    |   |-- state.hrd
    |   `-- template.hrd
    `-- test!test
        |-- actions.py
        |-- instance.hrd
        |-- instance_old.hrd
        |-- state.hrd
        `-- template.hrd

```

A service is also identified by its parent, so two services with the same domain/role/instance can exits if they have different parents.

This is useful for grouping services of a certain location/node together. Then, performing any action is made easier.



