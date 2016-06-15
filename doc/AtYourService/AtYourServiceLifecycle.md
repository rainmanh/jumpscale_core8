## Lifecycle of an AYS

- *Step1*: template
    - defines which files to use if not part of our sandbox (js8 sandbox)
      - this happens through code recipes (defines how to use code from e.g. gihub)
    - defines how to start/stop
    - defines how to monitor
    - defines how to backup/restore
    - defines any other relevant action which can be done on an ays service
    - this is stored in an ays template repo or in servicetemplates dir(inside *AYS repo*)


- *step2*:Blueprints
    - defines services that will be used or created
    - defines producers to be consumed (dependencies)  
    - defines parent services to be consumed  
    - defines attributes per service

- *Step3*: template gets converted to recipe
    - a recipe is copy of a template to the local ays repo
    - when a template get's chosen then it gets copied to the local ays repo
    - this is to make sure that we know exactly which templates (action files, ...) we used in that repo and can track change

- *Step4*: recipe gets converted to an ays instance = the init of the ays repo
    - is in aysrepo/services/.../$servicerole!$serviceinstance/
    - only the instance.hrd gets stored in this location, these are the configuration settings as they are used for this ays
    - they get born out of a schema: schema.hrd which is originated from template which became recipe, the schema defines the properties required for the instance.hrd

- *Step5*: deploy/manage an ays (install)
    - apply the changes to reality
    - this can be to populate a database
    - this can be to do an install
    - all types of actions now are possible on the ays instance
    - if a change happens in 1,2,3 or 4 this will have an automatic impact while installing
