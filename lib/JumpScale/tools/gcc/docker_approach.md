dockers are on top of aysfs

```
/aysfs/dockers/ro/caddy
/aysfs/dockers/rw/caddy
/aysfs/dockers/ro/etcd
/aysfs/dockers/rw/etcd
/aysfs/dockers/ro/skydns
/aysfs/dockers/rw/skydns
```


dockers have names caddy, etcd ...
they each mount 2 volumes
- 1 on .../ro/$name
- 1 on .../rw/$name

is our aydofs fuse layer
ro = readonly, rw = readwrite

they are mounted on /opt & /optvar  (volume mount docker)

the docker is our ubuntu 15.10 image with tmux inside (cuisine is now improved to also seamless support tmux)
so is X times the same docker image but mounted over other aysfs mounts (RO/RW)
