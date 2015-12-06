from JumpScale import j

def cb():
    from .Tmux import Tmux
    return Tmux()


j.sal._register('tmux', cb)
