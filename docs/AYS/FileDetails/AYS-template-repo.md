## AYS Template Repo

AYS template repositories contain all the metadata defining the life cycle of a service, from pre-installation to monitoring.

An example is [ays_jumpscale8](https://github.com/Jumpscale/ays_jumpscale8), defining the full life cycle of all JumpScale services.

You can configure which AYS template repositories to use in a configuration file:

    - Edit the file `/optvar/hrd/system/atyourservice.hrd`
    - Add a new section for every metadata repository you want to add:
    
    ```shell
    #domain=jumpscale, change name for other domains
    metadata.jumpscale             =
        branch:'master',
        url:'https://github.com/Jumpscale/ays_jumpscale8',

    #domain=openvcloud
    metadata.openvcloud        =
        url:'https://git.aydo.com/0-complexity/openvcloud_ays',
    ```

All metadata repositories are cloned as subdirectories of `/opt/code/$type/`:

  - Repositories from GitHub are cloned into `/opt/code/github`
    - So `https://github.com/Jumpscale/ays_jumpscale8` is cloned into `/opt/code/github/jumpscale/ays_jumpscale8`
  - Reposotories from other Git systems are cloned into `/opt/code/git/`
 

Each AYS service template has following files:
     
    * **schema.hrd** 
      * Which is the schema for the service instance metadata file (`instance.hrd`) relevant for an instance of the service
      * Contains information about how services interact with each other through:
          - Parenting, for more details see the section [Parents & Children](Definitions/Parents-Children.md)
          - Consumption, for more details see the section [Producers & Consumers](Definitions/Products-Consumers.md)
      * Has parameter definitions used to configure the service
      * Example:
          ```
            image = type:str default:'ubuntu'
            build = type:bool default:False
            build.url = type:str
            build.path = type:str default:''
            ports = type:str list

            sshkey = descr:'authorized sshkey' consume:sshkey:1:1 auto

            os = type:str parent:'os'
            docker = type:str consume:'app_docker':1 auto
            docker.local = type:bool default:False
          ```
         
    * **service.hrd** (optional)
      * Containing information about recurring action methods, how to react on changes and how to run processes
      * See [service.hrd](service.hrd) for more details
          
    * **actions.py** defines the behavior of the service (optional)