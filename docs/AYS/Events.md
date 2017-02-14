# AYS Events

AYS supports events in your services (managed by the `AYSDaemon`)

> `ays start` will run the ays daemon

## Example
Here we have a simple example around two actors `actproducer`, `actconsumer`, Where `actproducer` has a recurring action `every 5 seconds` and we want `actconsumer` to be able to listen on some events like
  - `producer_installed` which will be triggered after the `install` action
  - `new_msg_sent` which will be triggered `every 5 seconds`

### Actor producer
schema.hrd:

```yaml
msg = type:str default:'hello prince'
```
and recurring actions are defined in `actor.hrd`
actor.hrd
```yaml
recurring.send_message =
  period: '5s',
  log: True
```

`actions.py`
```python
def install(job):
    service = job.service
    print("Done installing the producer")
    redis_config = j.atyourservice.config['redis']
    command_queue = j.servers.kvs.getRedisStore("ays_server", namespace='db', **redis_config)
    payload = {"command": "event", "event": "producer_installed", "args":[""]}
    command_queue.queuePut("command", j.data.serializer.json.dumps(payload))


def send_message(job):
    service = job.service

    import time
    print("Sending message", service.model.data.msg)
    redis_config = j.atyourservice.config['redis']
    command_queue = j.servers.kvs.getRedisStore("ays_server", namespace='db', **redis_config)
    payload = {"command": "event", "event": "new_msg_sent", "args":[service.model.data.msg]}
    command_queue.queuePut("command", j.data.serializer.json.dumps(payload))
```

Please note: to fire a new event you need to push a `payload` on the command queue that consists of `command`=`event`, `event`=event_name, `args` is a list of event arguments.

### Actor Consumer
For the consumer
we can listen for the events in two ways


`action.py`

```python


def on_producer_installed1(job):
    args = job.model.args
    print("first handler::: was able to install the producer ... yay!!: ", args)

def on_producer_installed2(job):
    args = job.model.args
    print("second handler::: was able to install the producer ... yay!!: ", args)


def on_new_msg_sent(job):
    service = job.service
    args = job.model.args
    print("Got new message:  ", args)


```
#### 1- through init action

```python

def init(job):
    service = job.service
    # SET UP EVENT HANDLERS.
    handlers_map = [('producer_installed', 'on_producer_installed1'),
                    ('producer_installed', 'on_producer_installed2'),
                    ('new_msg_sent', 'on_new_msg_sent')]

    for (event, callback) in handlers_map:
        service.model.eventFilterSet(command=event, action=callback)
    service.saveAll()
```
blueprint:

```yaml
actproducer__p1:

actconsumer__c1:
```

#### 2- through blueprint
```yaml

actproducer__p1:

actconsumer__c1:

eventfilters:
  - cmd: producer_installed
    actor: actconsumer
    service: c1
    action: on_producer_installed1
  - cmd: producer_installed
    actor: actconsumer
    service: c1
    action: on_producer_installed2
  - cmd: new_msg_sent
    actor: actconsumer
    service: c1
    action: on_new_msg_sent

```
