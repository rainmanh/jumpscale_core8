# Walkthrough

## Creating AYS repository

Use the command <i>create_repo</i> to create the ays repository, specifying the github repo attached to it and the path where the repo will be created.<br>
The command will create a directory containing the following:
- <b>actorTemplates</b>: This folder contains all your locally created templates and their files.
- <b>blueprints</b>: Contains YAML files to define the nedded operations
- <b>services</b>:Contains services instances.
<br><br>
An example command:
	`ays create_repo -p {directory} -g {github repo url}`

## Creating an actor template
To create an actor {actor name}, you need to create a directory called {actor name} under <b>actorTemplates</b>. Each actor directory has to contain a schema.hrd file which contains the specification of the service instance and establish the relationships between itself and other services.
Parameter definition is as follows:

`{parameter name} = type:{type of parameter(int,str,..)} default:’{default value if none is specified}’`

To establish a  producer/consumer relationship with another service:

`image = type:str  default:’ubuntu’  consume:{service name}:{relationship}`

Where relationship specifies the  minimum number of instances it can relate to. For example {1:3}
means that each service can consume between one and three instance of the specified service.

Parent/children interaction:

`image = type:str  default:’ubuntu’  parent:{service name}`

actions.py defines the behavior of the service.

The function `install(job)` is executed when AYS is run and usually the main operations of the service is implemented inside that function.


To use the parameters of the service inside the file use the job object as follows:

```
def install(job):
    service = job.service
    arga = service.model.data

```
To access the parameters of the parent and/or producer:
```
parent = service.parent.model.data
appDocker = service.producers['app_docker'][0]
```
## Blueprints
Create a <a href = "www.yaml.org/start.html">YAML</a> file inside the blueprints directory. The file specifies the instances that need to be created from every actor as well as the actions that need to be executed, for example the `install()` function.
```
node.packet.net__kvm:
    client: 'main'
    project.name: 'fake_project_name'
    plan.type: 'Type 0'
    device.os: 'Ubuntu 16.04 LTS'
    location: 'Parsippany'
    sshkey: 'main'
    actions:
        - action: install
```
## Running the services
To create the services and schedule the actions run the command `ays blueprint`.<br>
The command `ays run` execute the functions specified in the blueprints files.<br>
Use `ays destroy` to reload the blueprints files.
