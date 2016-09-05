# Running JumpScale in a Sandbox

`js8`is a small command line tool that helps to install JumpScale 8 from scratch using the G8OS Virtual Filesystem.

## Installation of js8

js8 is a simple binary, written in Go.

You can downloads js8 and put the binary in your PATH location.

```shell
wget https://stor.jumpscale.org/storx/static/js8 -O /usr/local/bin/js8
chmod +x /usr/local/bin/js8
```

## Commands

Following commands are supported:

- **init** bootstraps your system and starts the FUSE layer
- **start** starts the FUSE layer
- **stop** stops the FUSE layer and unmounts it
- **reload** reloads the metatada
- **update** updates the metadata file, then reload

Below more details.

### init

`js8 init` will:

- Automatically install all packets required to run AYS File System, including

  - FUSE
  - tmux, or another startup manager if you specify that explicitelly since tmux is the default

- Download the AYF File Sytem binary and install it at `/usr/loca/bin/aysfs`

- Create a directory `/etc/ays/local/`
- Download the **js8_opt.flist** metadata file and put it at `/etc/ays/local/js8_opt.flist`
- Create a default configuration file at `/etc/ays/config.toml`

  - This default configuration uses <https://stor.jumpscale.org/storx/> as global store

- Add the -rw option to enable read/write support of the FUSE layer instead of read only

### start/stop

Starts and stops the AYS File System.

AYS File System supports 3 startup manager:

- tmux: lanch AYSfs in a tmux session
- systemd: install a service file in `/etc/systemd/system/aysfs.service` and use systemd to start/stop/reload AYSfs
- default: run the AYS File System directly. This will block on start

If you don't specify any startup manager, tmux is used.

### reload

This command ask AYS File System to reload the metadata file. Use it if you add/edit/remove some metadata files and want them to be reflected in the FUSE layer.

### update

Downloads the last version of JumpScale.flist from <https://stor.jumpscale.org/storx/static/js8_opt.flist> and put it at `/etc/ays/local/jumpscale.flist` then triggers a reload.

## build

how to build the js8 tool

- see: <https://github.com/Jumpscale/js8/blob/master/doc/build.md> -
