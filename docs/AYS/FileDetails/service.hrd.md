# AYS service.hrd

This is next to `schema.hrd` and the optional `actions.py` the `service.hrd` is another optional metadatafile for a service.

It contains information defining:

- Recurring action methods
- Register methods to events.

Below we discuss each of them.

## Recurring section

In the recurring section you define the actions to be executed on an recurring bases.

Example:

The service has 2 recurring actions, monitor and export. Monitor runs every minute and export once a day.

```
recurring.monitor = 1m
recurring.export = 1d
```

Following conditions apply for values used here:

- Only 3m, 3d and 3h (3 can be any integer value) or just an integer when you mean seconds
- In case of seconds, value should be at least 5

## Events subscription

A service can subscribe to 5 types of events:

- email: Execute an action when a mail is received.
- telegram: Execute an action when a message from [Telegram](telegram.org) is received
- alarm: Execute an action when an unexpected event happens
- eco: Execute an action when an error condition happens
- generic: The service receives an generic event object and need to manually decide to react to it or not.

Example of a service that register to two types of event. It will execute the escalate method from the actions.py file when a mail is received and the respond_telegram when a message from [Telegram](telegram.org) is received

```
events.mail =
    escalate,

events.telegram =
    respond_telegram,
```
