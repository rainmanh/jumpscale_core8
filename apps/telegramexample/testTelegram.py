import logging
from telegram.ext import Updater
from telegram.ext import CommandHandler
import os

from JumpScale import j

# info see
# https://pypi.python.org/pypi/python-telegram-bot

# to install lib:
# pip3 install python-telegram-bot --upgrade


def prepare():
    AUDIOFILE = "https://ia802508.us.archive.org/5/items/testmp3testfile/mpthreetest.mp3"
    STICKERFILE = "https://telegram-stickers.github.io/public/stickers/flags/8.png"
    url = "http://www.greenitglobe.com/en/images/logo.png"
    image = "%s/giglogo.png" % j.dirs.TMPDIR
    sound = "%s/test.mp3" % j.dirs.TMPDIR
    sticker = "%s/sticker.png" % j.dirs.TMPDIR
    j.sal.nettools.download(url, image, overwrite=False)
    j.sal.nettools.download(AUDIOFILE, sound, overwrite=False)
    j.sal.nettools.download(STICKERFILE, sticker, overwrite=False)


if "telegramkey" not in os.environ:
    print("example to set key:")
    print("export telegramkey=dfgaskdfhjgasdkfjbaskdljfbaskdjfb")
    raise RuntimeError("please et env variable: telegramkey")

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


key = os.environ["telegramkey"]


updater = Updater(token=key)
dispatcher = updater.dispatcher


def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

start_handler = CommandHandler('start', start)
# dispatcher.add_handler(start_handler)

# updater.start_polling()

from IPython import embed
print("DEBUG NOW ")
embed()
raise RuntimeError("stop debug here")

# DOWNLOAD SOME EXAMPLE FILES WHICH CAN BE USED


###############


# MAIN
################

bot.polling()


"""
in botfather do

/setcommands

and then paste

questions - answer some questions
pic - show image
sticker - show sticker
sound - audio
location - show dubai location
debug - go into ipshell in telegram robot on server

"""
