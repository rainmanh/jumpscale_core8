from JumpScale import j

def cb():
    from .CodeGenerator import CodeGenerator
    return CodeGenerator()


j.core._register('codegenerator', cb)
