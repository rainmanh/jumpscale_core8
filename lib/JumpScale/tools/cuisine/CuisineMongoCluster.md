# CuisineMongoClusterBuilder
It exposes a method `mongoCluster` that takes arguments:
* shards_ips
  * a list of ips of the shards
* config_ips
  * a list of ips of the config servers
* mongos_ips
  * a list of ips of the mongos instances
* unique = ""
  * a unique name to the cluster
* mongoport = None
  * the port to expose mongo daemons on
* dbdir = ""
  * the directory on which the data should be saved on each machine locally
* port = 22
  * the ssh port
* login = "root"
  * the machine login
* passwd = "rooter"
  * the machine password
