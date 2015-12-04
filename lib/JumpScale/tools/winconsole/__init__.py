from JumpScale import j

def cb():
    from .WinConsole import WinConsole
    return WinConsole()


j.tools._register('winconsole', cb)

