
from JumpScale import j





def ac():
    from .client import ACFactory
    return ACFactory()

j.clients._register('ac', ac)