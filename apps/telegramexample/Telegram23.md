# Telegram BOT

this page is not really unique to jumpscale, but is very useful to create your own robots on top of Jumpscale.

We use the excellent library from

- <https://pypi.python.org/pypi/python-telegram-bot>

## create your own bot on telegram

- go to your telegram chat app
- look for BotFather user (find user)
- in the chat screen do

```
/newbot
```

follow the instructions

```python
Kristof De Spiegeleer,
/newbot

BotFather,
Alright, a new bot. How are we going to call it? Please choose a name for your bot.

Kristof De Spiegeleer,
jumpscale

BotFather,
Good. Now let's choose a username for your bot. It must end in `bot`. Like this, for example: TetrisBot or tetris_bot.

Kristof De Spiegeleer,
jumpscale_bot

BotFather,
Done! Congratulations on your new bot. You will find it at telegram.me/jumpscale_bot. You can now add a description, about section and profile picture for your bot, see /help for a list of commands.

Use this token to access the HTTP API:
112176650:AAESzuAAAVIcrGdEgKY1YzZcymRp0i7n3s0

For a description of the Bot API, see this page: https://core.telegram.org/bots/api
```

## sample code

see [testTelegram](testTelegram.py)

now go to your chat app & look for user jumpscale_bot (ofcourse needs to be your chosen name)
