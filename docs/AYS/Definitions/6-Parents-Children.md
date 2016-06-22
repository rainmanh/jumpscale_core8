## Parents & Children

A service can be a parent for other services.

It's just a way of organizing your services and grouping them.

You will typically do it for inidicating some kind of child/parent relationship, e.g. an app living inside a node.

The parent/child relationship defines the location in the AYS repo directory structure (so purely visualization).

Child services also inherit their parent's executor defined in `getExecutor` by default.

Example of `parent` in `schema.hrd`:

```yaml
node = type:str parent:node auto
```

This means that the service has a parent of role `node` and that it should auto create its parent if it doesn't already exist. The `auto` tag is optional.

See the section [Parent/Child](../FileDetails/Parent-Child.md) for more information on this topic.