# js8 cli

js8 is a small tool that helps to install jumpscale8 from scratch using the [AYSfs](/AtYourService/AYS FS.md)

## Installation of js8
js8 is a simple go binary, so you can downloads it and put the binary in your PATH location.
```
wget https://stor.jumpscale.org/storx/static/js8 -O /usr/local/bin/js8
chmod +x /usr/local/bin/js8
```

## Commands
- init - will bootstrap you system and start the fuse layer
- start - start the fuse layer
- stop - stop the fuselayer and unmount it
- reload - reload the metatada
- update - update the metadata file, then reload

### init
```js8 init``` will: 
- install will automatically install the packet required to run AYSfs.
The dependecies are :
 - fuse
 - tmux, only if you choose to use tmux as the startup manager for AYSfs. tmux is the default.
- download AYFfs binary and instll it at ```/usr/loca/bin/aysfs```
- create a directory the ```/etc/ays/local/```
- download the *js8_opt.flist* metadata file and put it at ```/etc/ays/local/js8_opt.flist```
- create a default configuration file at ```/etc/ays/config.toml```
    - the default configuration use https://stor.jumpscale.org/storx/ as global store.  
- add the -rw option to enable read/write support of the fuse layer instead of read only.

### start/stop
Start and stop AYSfs
AYSfs supports 3 startup manager.
- tmux : lanch AYSfs in a tmux session
- systemd : install a service file in ```/etc/systemd/system/aysfs.service``` and use systemd to start/stop/reload AYSfs
- default : run the AYSfs directly. This will block on start

If you don't specify any startup manager, tmux is used.

### reload
This command ask AYSfs to reload the metadata file. use it if you add/edit/remove some metadata file and want them to be reflected in the fuse layer.

### update
Downloads the last version of jumpscale.flist from https://stor.jumpscale.org/storx/static/js8_opt.flist and put it at ```/etc/ays/local/jumpscale.flist``` then triggers a reload.