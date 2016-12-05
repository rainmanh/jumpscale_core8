# Delete

```
Usage: ays delete [OPTIONS]

  Delete a service and all its children.
  Be carefull with this action, there is no come back once a service is deleted.

Options:
  -r, --role TEXT      optional role for ays instances you want to delete
  -i, --instance TEXT  optional name of instance
  --ask                ask confirmation before delete services
  --help               Show this message and exit.
```

Example:
```
$ ays delete -r vdc
Services selected for deletion:
- service:vdc!autosnapshot

child that will also be deleted:
  - service:autosnapshotting!main
- service:vdcfarm!auto_1

child that will also be deleted:
  - service:vdc!autosnapshot

Are you sure you want to delete ? (y/n):
```
It will prompt a confirmation message before deleting any service so you have a chance to validate your action before executing it.
