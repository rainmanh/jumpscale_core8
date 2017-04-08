<!-- toc -->
## j.data.time

- /opt/jumpscale8/lib/JumpScale/data/time/Time.py
- Properties
    - timeinterval

### Methods

generic provider of time functions
lives at j.data.time

#### HRDateTime2epoch(*hrdatetime*) 

```
convert string date/time to epoch
Needs to be formatted as 16/06/1988 %H:%M:%S

```

#### HRDatetoEpoch(*datestr, local=True*) 

```
convert string date to epoch
Date needs to be formatted as 16/06/1988

```

#### any2HRDateTime(*val*) 

```
if list will go item by item until not empty,0 or None
if int is epoch
if string is human readable format
if date.time yeh ...

```

#### any2epoch(*val, in_list*) 

```
if list will go item by item until not empty,0 or None
if int is epoch
if string is human readable format
if date.time yeh ...

```

#### epoch2HRDate(*epoch, local=True*) 

#### epoch2HRDateTime(*epoch, local=True*) 

#### epoch2HRTime(*epoch, local=True*) 

#### epoch2ISODateTime(*epoch*) 

#### epoch2pythonDate(*epoch*) 

#### epoch2pythonDateTime(*epoch*) 

#### fiveMinuteIdToEpoch(*fiveMinuteId*) 

#### formatTime(*epoch, formatstr='%Y/%m/%d %H:%M:%S', local=True*) 

```
Returns a formatted time string representing the current time

See http://docs.python.org/lib/module-time.html#l2h-2826 for an
overview of available formatting options.

@param format: Format string
@type format: string

@returns: Formatted current time
@rtype: string

```

#### get5MinuteId(*epoch*) 

```
is # 5 min from jan 1 2010

```

#### getDayId(*epoch*) 

```
is # day from jan 1 2010

```

#### getDeltaTime(*txt*) 

```
only supported now is -3m, -3d and -3h (ofcourse 3 can be any int)
and an int which would be just be returned
means 3 days ago 3 hours ago
if 0 or '' then is now

```

#### getEpochAgo(*txt*) 

```
only supported now is -3m, -3d and -3h  (ofcourse 3 can be any int)
and an int which would be just be returned
means 3 days ago 3 hours ago
if 0 or '' then is now

```

#### getEpochFuture(*txt*) 

```
only supported now is +3d and +3h  (ofcourse 3 can be any int)
+3d means 3 days in future
and an int which would be just be returned
if txt==None or 0 then will be 1 day ago

```

#### getHourId(*epoch*) 

```
is # hour from jan 1 2010

```

#### getLocalTimeHR() 

```
Get the current local date and time in a human-readable form

```

#### getLocalTimeHRForFilesystem() 

#### getMinuteId(*epoch*) 

```
is # min from jan 1 2010

```

#### getSecondsInHR(*seconds*) 

#### getTimeEpoch() 

```
Get epoch timestamp (number of seconds passed since January 1, 1970)

```

#### getTimeEpochBin() 

```
Get epoch timestamp (number of seconds passed since January 1, 1970)

```

#### pythonDateTime2Epoch(*pythonDateTime, local=True*) 

#### pythonDateTime2HRDateTime(*pythonDateTime, local=True*) 


```
!!!
title = "J.data.time"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.data.time"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.data.time"
date = "2017-04-08"
tags = []
```
