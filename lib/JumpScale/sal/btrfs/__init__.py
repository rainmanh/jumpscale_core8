from JumpScale import j


def cb():
    from .BtrfsExtension import BtrfsExtension
    return BtrfsExtension()


j.sal._register('btrfs', cb)
