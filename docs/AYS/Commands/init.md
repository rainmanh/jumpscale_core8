# Init

The `init` command will see what needs to be done and detect all changes to the system.

```shell
ays init --help
Usage: ays init [OPTIONS]

  ==== BASE ====

      When using data the data is passed to the specific instance, if data used also role and instance needs to be used

      Step 1: init will walk over all existing recipes (AYS service templates in local context) and will see if recipe actions or HRDs changed

      if there is change than all ays instance originating from this recipe\'s state will be changed this will allow the further install action to execute on the change

      if there is change in hrd then: 
      - change_hrd_template() on the ays instance actions is called

      if there is change in the actions methods then: 
      - change_method() on the ays instance actions is called. This allows action to manipulate the ays tree as result of change

      Step 2: init will walk over all existing ays instances, and detect if instance.hrd got changed

      if change than the change will be marked in the state file

      if change in hrd then
      - change_hrd_instance() will be called on ays instance actions

      REMARK: blueprints are no longer processed in init step, use the ays blueprint command


Options:
  -r, --role TEXT      optional role for ays instances to init
  -i, --instance TEXT  optional name of instance
  -d, --data TEXT      data to populate a specific instance
  --help               Show this message and exit.
`
```

Data can be passed to the `init` command to fill in the HRDs. In that case `role` and `instance` needs to be specified.

If no data is passed then questions will be asked to fill in the HRD.

```shell
ays init -r redis -i system --data 'param.name:system param.port:7766 param.disk:0  param.mem:100 param.ip:127.0.0.1 param.unixsocket:0 param.passwd:'
```

What ever you pass with `--data` is used to populate the HRD files of the service instances.
