<!-- toc -->
## j.tools.aggregator

- /opt/jumpscale8/lib/JumpScale/tools/aggregator/Aggregator.py

### Methods

    

#### getClient(*redisConnection, nodename*) 

#### getTester() 

```
The tester instance is used to test stats aggregation and more.

Example usage:
redis = j.clients.redis.get('localhost', 6379)
agg = j.tools.aggregator.getClient(redis, 'hostname')
influx = j.clients.influxdb.get()
tester = j.tools.aggregator.getTester()

print(tester.statstest(agg, influx, 1000))

this test should print something like

####################
Minutes: 5
Avg Sample Rate: 6224
Test result: OK
####################
Expected values:
Sun Feb 21 09:56:27 2016: 516.612
Sun Feb 21 09:57:27 2016: 505.787
Sun Feb 21 09:58:27 2016: 401.824
Sun Feb 21 09:59:27 2016: 397.15
Sun Feb 21 10:00:27 2016: 497.779
Reported values:
Sun Feb 21 09:56:00 2016: 516.612
Sun Feb 21 09:57:00 2016: 505.787
Sun Feb 21 09:58:00 2016: 401.824
Sun Feb 21 09:59:00 2016: 397.15
Sun Feb 21 10:00:00 2016: 497.779
ERRORS:
No Errors

:return: Report as string

```


```
!!!
title = "J.tools.aggregator"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.tools.aggregator"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.tools.aggregator"
date = "2017-04-08"
tags = []
```
