<!-- toc -->
## j.core.platformtype.myplatform.executor.cuisine.solutions.mongocluster

- /opt/jumpscale8/lib/JumpScale/tools/cuisine/solutions/CuisineMongoCluster.py
- Properties
    - cuisine

### Methods

#### createCluster(*executors, numbers*) 

```
@param executors

e.g.
e1=j.tools.executor.getSSHBased(addr="10.0.3.65", port=22, login="root", passwd="rooter")
e2=j.tools.executor.getSSHBased(addr="10.0.3.254", port=22, login="root", passwd="rooter")
e3=j.tools.executor.getSSHBased(addr="10.0.3.194", port=22, login="root", passwd="rooter")
executors=[e1,e2,e3]

@param numbers
a tuple containing the number of shards, config servers, mongos instances
and nodes per shards' replica set
>>> numbers=(4, 2, 1, 2)
means 4 hards with two replica sets, 2 config servers, 1 mongos instance
if not passed it will be (len(executors) - 2, 1, 1, 1)

```

#### mongoCluster(*shards_nodes, config_nodes, mongos_nodes, shards_replica_set_counts=1*) 

```
shards_nodes: a list of executors of the shards
config_nodes: a list of executors of the config servers
mongos_nodes: a list of executors of the mongos instanses
shards_replica_set_count: the number of nodes in a replica set in the shards
you can find more info here https://docs.mongodb.com/manual/tutorial/deploy-shard-cluster/

```

