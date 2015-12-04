from JumpScale import j

def cb():
    from .qemu_img import QemuImg
    return QemuImg()


j.sal._register('qemu_img', cb)

