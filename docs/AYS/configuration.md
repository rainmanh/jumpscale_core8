# AtYourService configuration

Now that AYS use a database to store it's data, we need to be able to configure the connection to this database.  
To do so we use a simple configuration file. It need to be located in `/optvar/cfg/ays/ays.conf`

In this file you need to specify how AYS need to connect to redis. It supports two mode, TCP or UNIX socket.

Here are two example of configuration file.
For TCP:
```toml
[redis]
host = "localhost"
port = 6379
```

For unix socket
```toml
[redis]
unixsocket = '/var/run/redis.sock'
```

If no configuration file exists, the default behavior is to try to connect to redis using a unix socket located at `/tmp/ays.sock`


## Redis server configuration
By default redis is an in-memory only key value store. But for our use case we want the data to be persistent event after the server has stopped. To do that we need to configure the redis server to save its data on disk.

Here is an example of valid redis configuration for AYS:
```
# disable listening on tcp socket
port 0

# specify location of the unixsocket
unixsocket /tmp/ays.sock

# change location where to dump the database files
dir /optvar/data/redis-server

# By default Redis asynchronously dumps the dataset on disk. This mode is
# good enough in many applications, but an issue with the Redis process or
# a power outage may result into a few minutes of writes lost (depending on
# the configured save points).
#
# The Append Only File is an alternative persistence mode that provides
# much better durability. For instance using the default data fsync policy
# (see later in the config file) Redis can lose just one second of writes in a
# dramatic event like a server power outage, or a single write if something
# wrong with the Redis process itself happens, but the operating system is
# still running correctly.
#
# AOF and RDB persistence can be enabled at the same time without problems.
# If the AOF is enabled on startup Redis will load the AOF, that is the file
# with the better durability guarantees.
#
# Please check http://redis.io/topics/persistence for more information.
appendonly yes
```
