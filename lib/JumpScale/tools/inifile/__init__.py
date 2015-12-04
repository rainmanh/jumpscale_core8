from JumpScale import j

def cb():
    from .IniFile import InifileTool
    return InifileTool()


j.tools._register('inifile', cb)
