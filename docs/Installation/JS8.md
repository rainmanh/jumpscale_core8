# Running JumpScale in a Sandbox

`js8` is a small command line tool that helps to install JumpScale 8 from scratch using the G8OS Virtual Filesystem.

## Installation of js8

js8 is a simple binary, written in Go.

You can download js8 and put the binary in your PATH location:

```shell
wget https://stor.jumpscale.org/storx/static/js8 -O /usr/local/bin/js8
chmod +x /usr/local/bin/js8
```

## Commands

Following commands are supported:

- **init** bootstraps your system and starts the FUSE layer
- **start** starts the FUSE layer
- **stop** stops the FUSE layer and then unmounts it
- **reload** reloads the metadata
- **update** updates the metadata file, then reloads the metadata

Below more details.

### init

`js8 init` will:

- Automatically install all packets required to run the AYS filesystem, including:

  - FUSE
  - tmux or another startup manager if you specify that explicitly; tmux is the default

- Download the AYF Filesystem binary and install it at `/usr/loca/bin/aysfs`

- Create a directory `/etc/ays/local/`
- Download the **js8_opt.flist** metadata file and put it at `/etc/ays/local/js8_opt.flist`
- Create a default configuration file at `/etc/ays/config.toml`

  - This default configuration uses <https://stor.jumpscale.org/storx/> as global store

- Add the ```-rw``` option to enable read/write support of the FUSE layer instead of read only

### start/stop

Starts and stops the AYS filesystem.

Three startup managers are supported, use one of the below options to indicate which one you want:

- **tmux** launches the AYS filesystem in a tmux session
- **systemd** install a service file in `/etc/systemd/system/aysfs.service` and uses **systemd** to start/stop/reload the AYS filesystem
- **default** runs the AYS filesystem directly; this will block on start

If you don't specify any startup manager, tmux is used.

### reload

This command asks the AYS filesystem to reload the metadata file. Use it if you added, edited or removed some metadata files and want them to be reflected in the FUSE layer.

### update

Downloads the latest version of **JumpScale.flist** from https://stor.jumpscale.org/storx/static/js8_opt.flist, puts it at `/etc/ays/local/jumpscale.flist`, and then triggers a reload.

```
!!!
title = "JS8"
date = "2017-04-08"
tags = []
```
