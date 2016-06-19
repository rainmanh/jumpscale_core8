
Protocol used on stdout
-----------------------


    10:: key:value|type[|@flag]

Currently supported message types:

* `kv` - Simple Key/Value.
* `g`  - Gauge, similar to `kv` but only the last value per key is retained
* `ms` - Timer.
* `c`  - Counter.
* `s`  - Unique Set

After the flush interval, the counters and timers of the same key are
aggregated and this is sent to the agent controller.

Gauges also support "delta" updates, which are supported by prefixing the
value with either a `+` or a `-`. This implies you can't explicitly set a gauge to a negative number without first setting it to zero.

Examples:

The following is a simple key/value pair, in this case reporting how many
queries we've seen in the last second on MySQL::

    10:: mysql.queries:1381|kv

The following is a timer, timing the response speed of an API call::

    10:: api.session_created:114|ms

The next example is increments the "rewards" counter by 1::

    10:: rewards:1|c

Here we initialize a gauge and then modify its value::

    10:: inventory:100|g
    10:: inventory:-5|g
    10:: inventory:+2|g

Sets count the unique items, so if statsite gets::

    10:: users:abe|s
    10:: users:zoe|s
    10:: users:bob|s
    10:: users:abe|s

Then it will emit a count 3 for the number of uniques it has seen.

# Sending data to stats aggregator
Stats data is always of the form of (key, value) pair where key represents the name of value (cpu usage, mem usage, space usage, etc...) and the value is always a `float` number.

There are 2 ways to send stats data to the stats aggregator depends on where you are living inside the Agent controller. 

For internal components that generates stats messages, you get reference to the stats aggregator and then you can call one of the `KeyValue`, `Gauage`, `Counter`, `Timer` or `Set` methods to feed the stats data. Already the process manager does this to feed the `cpu` and `mem` usage of the external processes.

On the other hand for external processes/script, they just need to write stats messages on the correct log level.

An external script can output stats messages to its `stdout` as following

```bash
10::custom.stats.key:1.0|g
10::custom.stats.key:2.2|g
10::custom.stats.key:2.0|g
```

- The agent logging system will intercept the stats messages, and send it to the stats aggregator as they come in.
- The stats aggregator will buffer the messages, until it's time to do the aggregation/flushing (based on configuration or command arguments)
- Stats aggregator will flush aggregated values with aligned timestamp to the AC `/stats` endpoint.
- AC currently dumps the data to `influxdb` (not fully tested at the moment of writing this wiki).

## Stats Aggregator Settings
For more details about the agent configuration please check [[Agent Configuration]] page

```toml
[stats]
Interval = 60 # seconds
```
According to the configuration snippet, Stats aggregator will aggregate/flush stats messages every 60 seconds.  This means to graph real-time graphs for certain statistics, values can be drawn directly from `influxdb`.

> Note that, Aggregation/flushing interval can be set explicitly by the command itself, in that case the interval value will be overridden for that command.
> Note: An optimum `Interval` of 300 seconds (5min) is recommended.