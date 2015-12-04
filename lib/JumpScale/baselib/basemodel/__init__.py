from JumpScale import j

def cb():
    from .BaseModelFactory import BaseModelFactory
    return BaseModelFactory()


j.core._register('models', cb)
