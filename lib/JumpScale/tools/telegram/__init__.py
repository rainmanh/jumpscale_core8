from JumpScale import j

def cb1():
    from .TelegramFactory import TelegramFactory
    return TelegramFactory()


j.tools._register('telegrambot', cb1)


j.tools.connection=None
