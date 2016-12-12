from datetime import datetime


from JumpScale import j

AUDIOFILE = "https://ia802508.us.archive.org/5/items/testmp3testfile/mpthreetest.mp3"
STICKERFILE = "https://telegram-stickers.github.io/public/stickers/flags/8.png"


class DemoHandler:

    def __init__(self):
        url = "http://www.greenitglobe.com/en/images/logo.png"
        self.image = "%s/giglogo.png" % j.dirs.TMPDIR
        self.sound = "%s/test.mp3" % j.dirs.TMPDIR
        self.sticker = "%s/sticker.png" % j.dirs.TMPDIR
        j.sal.nettools.download(url, self.image, overwrite=False)
        j.sal.nettools.download(AUDIOFILE, self.sound, overwrite=False)
        j.sal.nettools.download(STICKERFILE, self.sticker, overwrite=False)
        self.once = True

    def on_text(self, tg, message):
        if self.once:
            print(tg.send_message(message.chat.id, "Welcome to the demo bot"))
            print("send init photo")
            print(tg.send_photo(message.chat.id, self.image, reply_to_message_id="", reply_markup=""))
            print("photo send")
            self.once = False

        markup = {}
        markup["keyboard"] = [["yes"], ["no"], ["stop"], ["send photo", "send sticker", "send sound"]]
        markup["resize_keyboard"] = True
        markup["one_time_keyboard"] = True

        if message.text == "send photo":
            print(tg.send_photo(message.chat.id, self.image, reply_to_message_id="", reply_markup=""))
        if message.text == "send sticker":
            result = tg.send_sticker(message.chat.id, self.sticker, reply_to_message_id="", reply_markup="")
            print(result)
        if message.text == "send sound":
            print(tg.send_audio(message.chat.id, self.sound, reply_to_message_id="", reply_markup=""))
        elif not message.text == "stop":
            print(tg.send_message(message.chat.id, "Please fill in", reply_to_message_id=None,
                                  reply_markup=j.data.serializer.json.dumps(markup)))
