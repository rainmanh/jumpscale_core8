# Blueprint

The `blueprint` command will create all AYS service instances required for the application described by the blueprint.

```shell
ays blueprint --help
Usage: ays blueprint [OPTIONS] [PATH]

  will process the blueprint(s) pointed to

  it path is directory then all blueprints in directory will be processed
  (when not starting with _) if is file than only that 1 file

  if path=="" then blueprints found in $aysdir/blueprints will be processed

  if role & instance specified then only the ays instances with specified
  role/instance will be processed

Options:
  -r, --role TEXT      optional role for ays instances to init
  -i, --instance TEXT  optional name of instance
  --help               Show this message and exit.
```
