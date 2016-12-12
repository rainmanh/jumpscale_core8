import logging
import telegram
from telegram.error import NetworkError, Unauthorized
import os
import time
from JumpScale import j

# info see
# https://pypi.python.org/pypi/python-telegram-bot

# to install lib:
# pip3 install python-telegram-bot --upgrade


if "telegramkey" not in os.environ:
    print("example to set key:")
    print("export telegramkey=dfgaskdfhjgasdkfjbaskdljfbaskdjfb")
    raise RuntimeError("please et env variable: telegramkey")

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def main():
    key = os.environ["telegramkey"]
    global update_id
    # Telegram Bot Authorization Token
    bot = telegram.Bot(key)

    # get the first pending update_id, this is so we can skip over it in case
    # we get an "Unauthorized" exception.
    try:
        update_id = bot.getUpdates()[0].update_id
    except IndexError:
        update_id = None

    while True:
        try:
            echo(bot)
        except NetworkError:
            time.sleep(1)
        except Unauthorized:
            # The user has removed or blocked the bot.
            update_id += 1


def echo(bot):
    global update_id
    # Request updates after the last update_id
    for update in bot.getUpdates(offset=update_id, timeout=10):
        # chat_id is required to reply to any message
        chat_id = update.message.chat_id
        update_id = update.update_id + 1

        if update.message:  # your bot can receive updates without messages

            if update.message.document != None:
                ff = bot.getFile(update.message.document.file_id)
                path = "%s/%s" % (j.dirs.TMPDIR, update.message.document.file_name)
                ff.download(path)

            from IPython import embed
            print("DEBUG NOW ooo")
            embed()

            # Reply to the message
            update.message.reply_text(update.message.text)


if __name__ == '__main__':
    main()
