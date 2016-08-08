## Blueprint

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

The process that takes places is:

- Copy the AYS service template files to appropriate destination in your AYS repository
  - e.g. `/Users/kristofdespiegeleer1/code/jumpscale/ays_core_it/services/sshkey!main`)
- Call the `actions.input`
    - Goal is to manipulate the arguments which are the basis of the `instance.hrd`, this allows the system to avoid questions to be asked during installations (because of @ASK statements in the `instance.hrd` files)
    - In `actions.input` manipulate the `args` argument to the method
    - Return `True` if action was ok
    - Ask the non configured items from `schema.hrd` (the @ASK commands, the ones not filled in in previous step
- Call `actions.hrd`
    - Now the @ASK is resolved and the input arguments are set, this step allows to further manipulate the HRD files
       - Example: create an SSH key and store in HRD file
    - After this action the AYS directory is up to date with all required configuration information
    - Information outside can be used to get info in HRD, e.g. stats info from Reality DB
- Apply all instance and `service.hrd` arguments on the action files in the deployed AYS service instance directory
    - This means that all action files have all template arguments filled in
