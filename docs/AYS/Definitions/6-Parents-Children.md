## Parents & Children

There is a special type of consumption which is called a *parent*.

This defines the location in the AYS repo file system (visualization) but also a child/parent relationship, e.g. an app living inside a node.

Child services also inherit their parent's executor defined in `getExecutor` by default.

Example of parents in `schema.hrd`:

```yaml
node = type:str parent:node auto
```

This means that the service has a parent of role `node` and that it should auto create its parent if it doesn't already exist. The `auto` tag is optional.