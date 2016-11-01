# Do

The `do` command if for calling an action of a service instance.

```shell
ays do --help
Usage: ays do [OPTIONS] ACTION

  call an action (which is a method in the action file e.g.
  start/stop/export/...)

Options:
  -r, --role TEXT       optional role for ays instances execute an action on
  -i, --instance TEXT   optional name of instance
  --force               force execution even if no change
  --producerroles TEXT  roles of producers which will be taken into
                        consideration, if * all
  --ask                 ask on which service to execute the action
  --help                Show this message and exit.
```
