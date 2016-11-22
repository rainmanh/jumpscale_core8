# Setstate

```shell
Usage: ays set_state [OPTIONS] ACTION

  Manually set the state of an action. You can filter on which services to
  apply the state using --role and --instance Only use this command if you
  know what you're doing !!

Options:
  --state TEXT     state to set, can be: new, ok, scheduled
  --role TEXT      optional role for ays instances execute an action on
  --instance TEXT  optional name of the service
  --help           Show this message and exit.
```
