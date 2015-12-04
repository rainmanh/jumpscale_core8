from JumpScale import j

def cb():
    from .Cuisine2 import OurCuisineFactory
    return OurCuisineFactory()


j.tools._register('cuisine', cb)
