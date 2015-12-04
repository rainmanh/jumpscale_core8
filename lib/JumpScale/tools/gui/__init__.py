from JumpScale import j

def cb():
    from .Gui import Gui
    return Gui()


j.tools._register('gui', cb)
