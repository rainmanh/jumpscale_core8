## Install

The 'install' command makes the service instances relatity, actually installing everything.

```shell
ays install --help
Usage: ays install [OPTIONS]

  make the ays instances reality (install) if you want more finegrained
  controle please use the do cmd e.g. to start, ...

Options:
  --role TEXT           optional role for ays instances execute an action on
  --instance TEXT       optional name of instance
  --force               if True then will ignore state of service action.
  --producerroles TEXT  roles of producers which will be taken into
                        consideration, if * all
  --ask                 ask on which service to execute the action
  --help                Show this message and exit.
```