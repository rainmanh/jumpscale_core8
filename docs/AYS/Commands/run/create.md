# ays run create

```shell
ays run create --help
Usage: ays run create [OPTIONS]

  Look for all action with a state 'schedule', 'changed' or 'error' and
  create a run. A run is an collection of actions that will be run on the
  repository.

Options:
  --ask         ask before confirmation before executing
  --force       force execution even if no change
  --debug       enable debug in jobs
  --profile     enable profiling of the jobs
  -f, --follow  follow run execution
  --help        Show this message and exit.
```
