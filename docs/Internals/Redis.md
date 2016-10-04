# System Redis

For more advanced usecases and for performance Jumpscale depends on Redis.

Redis is an open source (BSD licensed), in-memory data structure store, used as database, cache and message broker.

## Used for what functions?

- Logs and log rotation
- Error conditions
- Statistics and aggregation of statistics
- Queuing work to local worker processes (workers)
- Caching of configuration parameters
- Remembering state of e.g. executors
- ...

## How does it get loaded?

- When initiating a j instance, whether by starting a jsshell or importing j from JumpScale, it will be loaded on j.core.db
- First port 9999 will be checked, if available that client will be loaded
- Then default Redis port 6379 will be checked and loaded if found
- Otherwise j.core.db=None
