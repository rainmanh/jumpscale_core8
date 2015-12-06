from JumpScale import j

def cb():
    from .ExecutorFactory import ExecutorFactory
    return ExecutorFactory()

j.base.loader.makeAvailable(j, 'tools')
j.tools._register('executor', cb)
