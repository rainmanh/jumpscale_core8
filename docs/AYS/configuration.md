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
