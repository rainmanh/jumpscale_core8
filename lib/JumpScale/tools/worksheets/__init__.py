from JumpScale import j

def cb():
    from .Sheets import Sheets
    return Sheets()


j.tools._register('worksheets', cb)

