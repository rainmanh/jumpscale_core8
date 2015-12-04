from JumpScale import j

def cb():
    from .BackupFactory import BackupFactory
    return BackupFactory



j.tools._register('backup_vfs', cb)
