<!-- toc -->
## j.sal.cloudfs

- /opt/jumpscale8/lib/JumpScale/baselib/cloudsystemfs/CloudSystemFS.py
- Properties
    - logger

### Methods

#### copyDir(*sourcepath, destinationpath, tempdir='/tmp', recursive=True*) 

```
Copy Directory

```

#### copyFile(*sourcepath, destinationpath, tempdir='/tmp'*) 

```
export specified file to destination
TODO: needs to be copied onto cloudapi aswell

@param sourcepath: location of the file to export
@type sourcepath: string

@param destinationpath: location to export the file to. e.g.
    cifs://login:passwd@10.10.1.1/systemnas
@type destinationpath: string

```

#### exportDir(*sourcepath, destinationpath, recursive=True, tempdir='/tmp'*) 

```
export specified folder to destination
TODO: needs to be copied onto cloudapi aswell

@param sourcepath:       location to export. e.g.
    ftp://login:passwd@10.10.1.1/myroot/drive_c_kds.vdi
@type sourcepath:        string

@param destinationpath:  location to export the dir to
@type destinationpath:   string

@param recursive:        if true will include all sub-directories
@type recursive:         boolean

```

#### exportVolume(*sourcepath, destinationpath, format='vdi', tempdir='/tmp'*) 

```
export volume to a e.g. VDI

@param sourcepath:         device name of the volume to export e.g.  E: F on windows, or
    /dev/sda5 on linux
@type sourcepath:          string

@param destinationpath:    location to export the volume to e.g.
    ftp://login:passwd@10.10.1.1/myroot/mymachine1/test.vdi, if .vdi.tgz at end then
    compression will happen automatically
@type destinationpath:     string
@param tempdir:            (optional) directory to use as temporary directory, for
    cifs/smb tempdir can be None which means: export directly over CIFS
@type tempdir:             string

```

#### fileGetContents(*url*) 

#### importDir(*sourcepath, destinationpath, tempdir='/tmp'*) 

```
import specified dir to machine path
TODO: needs to be copied onto cloudapi aswell

@param sourcepath: location to import the dir from. e.g.
    ftp://login:passwd@10.10.1.1/myroot/mymachine1/
@type sourcepath: string

@param destinationpath: location to import the dir to (i.e.full path on machine)
@type destinationpath: string

```

#### importFile(*sourcepath, destinationpath, tempdir='/tmp'*) 

```
import specified file to machine path
TODO: needs to be copied onto cloudapi aswell

@param sourcepath: location to import the file from. e.g.
    ftp://login:passwd@10.10.1.1/myroot/drive_c_kds.vdi
@type sourcepath: string

@param destinationpath: location to import the file to (i.e.full path on machine)
@type destinationpath: string

```

#### importVolume(*sourcepath, destinationpath, format='vdi', tempdir='/tmp'*) 

```
Import volume from specified source

@param sourcepath: location to import the volume from e.g.
    ftp://login:passwd@10.10.1.1/myroot/mymachine1/test.vdi, if .vdi.tgz at end then
    compression will happen automatically
@type sourcepath: string

@param destinationpath: name of the device to import to e.g.  E: F on windows, or
    /dev/sda5 on linux
@type destinationpath: string
@param tempdir:            (optional) directory whereto will be exported; default is the
    default temp-directory as determined by underlying system
@type tempdir:             string

```

#### listDir(*path*) 

```
List content of specified path

```

#### moveDir(*sourcepath, destinationpath, tempdir='/tmp', recursive=True*) 

```
Move directory

```

#### moveFile(*sourcepath, destinationpath, tempdir='/tmp'*) 

```
Move a file

```

#### sourcePathExists(*sourcepath*) 

#### writeFile(*url, content*) 


```
!!!
title = "J.sal.cloudfs"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.sal.cloudfs"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.sal.cloudfs"
date = "2017-04-08"
tags = []
```
