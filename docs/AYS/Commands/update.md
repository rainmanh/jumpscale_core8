# Update

The `update` command is for making sure you are working on most recent data.

```shell
Usage: ays update [OPTIONS]

  Update actor to a new version. Any change detected in the actor will be
  propagated to the services and processChange method will be called all the
  way from actor to service instances.

Options:
  -n, --name TEXT  name of the actor to update
  --help           Show this message and exit.
```
