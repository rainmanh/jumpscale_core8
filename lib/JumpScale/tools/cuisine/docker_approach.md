dockers are on top of aysfs


TODO: *1 implement this 

they each mount 2 volumes

```
/aysfs/dockers/ro/$name
/aysfs/dockers/rw/$name
```


is our aydofs fuse layer
ro = readonly, rw = readwrite

they are mounted on /opt & /optvar  (volume mount docker) in the docker

the docker is our minimal ubuntu 15.10 image with tmux inside (cuisine is now improved to also seamless support tmux)
(there is almost nothing in the ubuntu installed, no python, ... (mc yes))

in future would be nice to have support for arch with real systemd inside but should run unprivileged (future)



