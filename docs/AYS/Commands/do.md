# Do

The `do` command is for calling an action of a service instance.

```shell
Usage: ays do [OPTIONS] ACTION

  Schedule an action then immediatly create a run. This is a shortcut from
  sending a blueprint with an actions block and the do `ays run`

Options:
  -r, --role TEXT           optional role for ays instances execute an action
                            on
  -i, --instance TEXT       optional name of instance
  --force                   force execution even if no change
  -p, --producerroles TEXT  roles of producers which will be taken into
                            consideration, if * all
  --args TEXT               argument to pass to the run. Can be a list of tags
                            e.g: "key:value key:value" or a path to a file
                            containing the argument. Format of the file can be
                            json, yaml, toml. format is detected using file
                            extension. default format is json
  --ask                     ask before confirmation before executing
  --debug                   enable debug in jobs
  --profile                 enable profiling of the jobs
  --help                    Show this message and exit.
```
