## cuisine.installer

The `cuisine.installer` module is responsible for installing JumpScale 8 in a sandbox mode. It contains a method `jumpscale8` which uses `aysfs` to get JumpScale to the target machine. Warning: it removes everything under `/opt`.

`cuisine.installer.jumpscale8` takes two parameters:

1. rw: to mount the fs as read-write. defaults to False
2. reset: reinstall jumpscale even if it exists. defaults to False 