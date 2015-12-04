from JumpScale import j

def cb():
    from .SerializersFactory import SerializersFactory
    return SerializersFactory()


j.data.serializer._register('serializers', cb)


def cb():
    from .SerializerInt import SerializerInt
    return SerializerInt()
j.data.serializer._register('int', cb)

def cb():
    from .SerializerTime import SerializerTime
    return SerializerTime()
j.data.serializer._register('time', cb)


def cb():
    from .SerializerBase64 import SerializerBase64
    return SerializerBase64()
j.data.serializer._register('base64', cb)

def cb():
    from .SerializerHRD import SerializerHRD
    return SerializerHRD()
j.data.serializer._register('hrd', cb)

def cb():
    from .SerializerDict import SerializerDict
    return SerializerDict()
j.data.serializer._register('dict', cb)

def cb():
    from .SerializerBlowfish import SerializerBlowfish
    return SerializerBlowfish()
j.data.serializer._register('blowfish', cb)

def cb():
    from .SerializerUJson import SerializerUJson
    return SerializerUJson()
j.data.serializer._register('json', cb)

def cb():
    from .SerializerYAML import SerializerYAML
    return SerializerYAML()
j.data.serializer._register('yaml', cb)



