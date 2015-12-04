from JumpScale import j

def cb():
    from .ProcessmanagerFactory import ProcessmanagerFactory
    return ProcessmanagerFactory()


j.core._register('processmanager', cb)
