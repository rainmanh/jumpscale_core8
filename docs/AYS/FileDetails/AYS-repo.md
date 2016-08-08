## AYS Repo

This is the main repository in which services are deployed, executed, ...

Following 4 directories are relevant in an AYS repo:


- **blueprints**
    - Contains blueprints (YAML files) defining what needs to be done

- **servicetemplates**
    - Local set of AYS service templates
    - AYS will always first look here for an AYS service template, and if not found here check the AYS configuration file (`/optvar/hrd/system/atyourservice.hrd`) as discussed above to know where to get the AYS service template

- **recipes**
    - Here all the local copies of the AYS service template are stored
    - From the AYS service recipes one or more service instances are created
    - Has no further meaning than being a local copy, this is done to be able to see changes in the template on local (Git) repo level

- **services**
    - Here the actual expanded services instances live
    - An `instance.hrd` file has all the info as required to make a deployment reality (install)
    - An `state.md` file which is the file which has all info related with states and results of the executing actions

