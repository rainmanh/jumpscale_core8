## Life Cycle of an AYS Service Instance

The life cycle of any service can be managed by AYS.


### Step 1: Create an AYS service template

A service becomes an AYS service when an AYS service template is created for that service.

An AYS service template defines:

    - Which files to use, this happens through code recipes, which define how to use code from e.g. GitHub
    - How to start/stop the service
    - How to monitor the service
    - How to backup/restore the service
    - Any other relevant action which can be done on the AYS service

An AYS service template is stored in an **AYS template repository** or locally in the `servicetemplates` directory of an **AYS repository**.


### Step 2: Create AYS blueprints using the AYS service

A service is typically deployed as part of a bigger solution, including other services, and that;s where the AYS Blueprint is used for.

An AYS blueprint defines:

    - Services that will be used or created
    - Producers to be consumed (dependencies)  
    - Parent services to be consumed  
    - Attributes per service


### Step 3: AYS service template gets "converted" into an AYS service recipe

An AYS service recipe is a copy of an AYS service template, residing in a local AYS repository.

So an AYS service template becomes an AYS service recipe when copied into the local AYS repository, where it will be used for actually deploying one or more instances of that service.


### Step 4: AYS service recipe gets "converted" into one or more AYS service instances

This happens when executing the `AYS init` command on the AYS repository.

What actually happens at that moment is that the `instance.hrd` for each of the service instances gets created in `ays-repo/services/.../$servicerole!$serviceinstance/`.

The `ìnstance.hrd` has all the configuration settings for that AYS service instance. All `instance.hrd` files get born out of the `schema.hrd` orginating from the service template which got "converted" to the service recipe. The schema defines the properties required for the `instance.hrd`.


### Step 5: Deploy & manage the AYS service instance

This is starts when you actually install the AYS service instance.

The installation 

    - Applies changes to reality
    - This can for instance be the provisioning of database content
    - All types of actions now are possible on the AYS service instance

If anything changes to what was described in the previous steps, this will automatically impact the instalation.