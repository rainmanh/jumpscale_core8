## Simulate

The `simulate` command does do the same as `ays do`, except it does not execute, it only shows what result would be.

```shell
ays simulate [OPTIONS] ACTION

  is like do only does not execute it, is ideal to figure out what would
  happen if you run a certain action

Options:
  --role TEXT           optional role for ays instances execute an action on
  --instance TEXT       optional name of instance
  --force               if True then will ignore state of service action.
  --producerroles TEXT  roles of producers which will be taken into
                        consideration, if * all
  --help                Show this message and exit.
```