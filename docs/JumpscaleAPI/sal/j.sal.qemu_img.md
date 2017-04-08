<!-- toc -->
## j.sal.qemu_img

- /opt/jumpscale8/lib/JumpScale/sal/qemu_img/Qemu_img.py

### Methods

#### commit(*fileName, diskImageFormat*) 

```
Commit the changes recorded in <fileName> in its base image.
@param fileName: a disk image filename
@param diskImageFormat: disk image format

```

#### convert(*fileName, diskImageFormat, outputFileName, outputFormat, compressTargetImage, encryptTargetImage, useCompatibilityLevel6, isTargetImageTypeSCSI, logger*) 

```
Convert the disk image <fileName> to disk image <outputFileName> using format
    <outputFormat>.
It can be optionally encrypted ("-e" option) or compressed ("-c" option).
Only the format "qcow" supports encryption or compression. The compression is read-only.
It means that if a compressed sector is rewritten, then it is rewritten as uncompressed
    data.

@param fileName: a disk image filename
@param diskImageFormat: disk image format
@param outputFileName: is the destination disk image filename
@param outputFormat: is the destination format
@param compressTargetImage: indicates that target image must be compressed (qcow format
    only)
@param encryptTargetImage: indicates that the target image must be encrypted (qcow format
    only)
@param useCompatibilityLevel6: indicates that the target image must use compatibility
    level 6 (vmdk format only)
@param isTargetImageTypeSCSI: indicates that the target image must be of type SCSI (vmdk
    format only)
@param logger: Callback method to report progress
@type logger: function

```

#### create(*fileName, diskImageFormat, size, baseImage, encryptTargetImage, useCompatibilityLevel6, isTargetImageTypeSCSI*) 

```
Create a new disk image <fileName> of size <size> and format <diskImageFormat>.
If base_image is specified, then the image will record only the differences from
    base_image. No size needs to be specified in this case. base_image will never be
    modified unless you use the "commit" monitor command.
@param fileName: a disk image filename
@param diskImageFormat: disk image format
@param size: the disk image size in kilobytes. Optional suffixes 'M' (megabyte) and 'G'
    (gigabyte) are supported
@param baseImage: the read-only disk image which is used as base for a copy on write
    image; the copy on write image only stores the modified data
@param encryptTargetImage: indicates that the target image must be encrypted (qcow format
    only)
@param useCompatibilityLevel6: indicates that the target image must use compatibility
    level 6 (vmdk format only)
@param isTargetImageTypeSCSI: indicates that the target image must be of type SCSI (vmdk
    format only)

```

#### info(*fileName, diskImageFormat, chain, unit='K'*) 

```
Give information about the disk image <fileName>. Use it in particular to know the size
    reserved on
disk which can be different from the displayed size. If VM snapshots are stored in the
    disk image,
they are displayed too.

@param fileName: a disk image filename
@param diskImageFormat: disk image format
@result: dict with info in KB

```


```
!!!
title = "J.sal.qemu Img"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.sal.qemu Img"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.sal.qemu Img"
date = "2017-04-08"
tags = []
```
