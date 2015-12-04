from JumpScale import j

def cb():
    from .SwaggerGen import SwaggerGen
    return SwaggerGen()


j.tools._register('swaggerGen', cb)
