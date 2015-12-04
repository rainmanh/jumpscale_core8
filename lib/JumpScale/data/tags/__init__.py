from JumpScale import j

def cb():
    from .TagsFactory import TagsFactory
    return TagsFactory()

j.data._register('tags', cb)
