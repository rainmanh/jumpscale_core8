# AYS Actions

- Manages the life cycle of your AYS
- you need to implement one or more methods (actions) on your atyourservice actions.py file

## Usage of arguments

Before the actions get executed AYS will apply the `instance.hrd` (as stored in AYS instance directory) on the `actions.py` file.

Example of an `instance.hrd`:

```python
description                    = 'life can be good in villa 77,\nIs for test purposes only.'
location                       = 'villa 78'
service.domain                 = 'ays'
service.name                   = 'datacenter'
service.version                =
```

In `actions.py` each `$(name)` will get replaced, e.g.:

```python
def somemethod(self):
  key = "$(service.domain)__$(service.name)__$(service.instance)"
  print(key)
```

This would print: `ays__datacenter_palmlab`

## Example:

**actions.py**:

These actions get executed when the AYS robot runs. This file is stored in the AYS template directory:

```python
class ActionsBaseMgmt:

    def change_hrd_template(self, service, originalhrd):
        for methodname, obj in service.state.methods.items():
            if methodname in ["install"]:
                service.state.set(methodname, "CHANGEDHRD")
                service.state.save()

    def change_hrd_instance(self, service, originalhrd):
        for methodname, obj in service.state.methods.items():
            if methodname in ["install"]:
                service.state.set(methodname, "CHANGEDHRD")
                service.state.save()

    def change_method(self, service, methodname):
        service.state.set(methodname, "CHANGED")
        service.state.save()

    def ask_telegram(self, username=None, message='', keyboard=[],
                     expect_response=True, timeout=120, redis=None, channel=None):
        """
        username: str, telegram username of the person you want to send the message to
        channel: str, telegram channel where the bot is an admin
        message: str, message
        keyboard: list of str: optionnal content for telegram keyboard.
        expect_response: bool, if you want to wait for a response or not. if True, this method retuns the response
            if not it return None
        timeout: int, number of second we need to wait for a response
        redis: redis client, optionnal if you want to use a specific reids client instead of j.core.db
        """
        redis = redis or j.core.db

        key = "%s:%s" % (username, j.data.idgenerator.generateGUID())

        out_evt = j.data.models.cockpit_event.Telegram()
        out_evt.io = 'output'
        out_evt.action = 'service.communication'
        out_evt.args = {
            'key': key,
            'username': username,
            'channel': channel,
            'message': message,
            'keyboard': keyboard,
            'expect_response': expect_response
        }
        redis.publish('telegram', out_evt.to_json())
        if expect_response:
            data = redis.blpop(key, timeout=timeout)
            if data is None:
                raise j.exceptions.Timeout('timeout reached')

            _, resp = data
            resp = j.data.serializer.json.loads(resp)
            if 'error' in resp:
                raise j.exceptions.RuntimeError('Unexpected error: %s' % resp['error'])

            return resp['response']

```
