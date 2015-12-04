from JumpScale import j

def cb():
    from .Params import ParamsFactory
    return ParamsFactory()

j.data._register('params', cb)
