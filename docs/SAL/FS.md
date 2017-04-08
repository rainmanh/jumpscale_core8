# FS

FS is short for filesystem. It helps you doing many filesystem-related operations.

## Accessing it

You can access `fs` as follows:

```python
j.sal.fs
```

We'll use it as `fs` for the rest of the document:

```python
fs = j.sal.fs
```

## Querying the system

You can query a lot of information about the system using helper functions like `sFile`, `isAsciiFile`, `isBinaryFile`, `isDir`, `isEmptyDir`, `isMount`, `validateFilename`, and `statPath`:

```python
In [2]: fs.isAsciiFile("/etc/hosts")
Out[2]: True

In [3]: fs.isBinaryFile("/bin/ls")
Out[3]: True

In [4]: fs.isAsciiFile("/bin/ls")
Out[4]: False

In [5]: fs.isFile("/")
Out[5]: False

In [6]: fs.isDir("/")
Out[6]: True
In [11]: fs.isEmptyDir("/")
Out[11]: False
In [12]: !mkdir emptydir
In [13]: fs.isEmptyDir("emptydir")
Out[13]: True

In [18]: fs.isMount("/proc")
Out[18]: True
In [19]: fs.isMount("emptydir/")
Out[19]: False
In [20]: fs.validateFilename("dasdas")
Out[20]: True

In [21]: fs.validateFilename("dasdas$as")
Out[21]: True

In [22]: fs.validateFilename("dasdas$::as")
Out[22]: True

In [23]: fs.validateFilename("dasdas$::?as")
Out[23]: True

In [28]: fs.validateFilename("dasdas$::%^as\0")
Out[28]: False

In [29]: fs.validateFilename("dasdas$::%^as/1")
Out[29]: False
In [33]: fs.getcwd()
Out[33]: '/tmp'

In [34]: fs.fileSize("/bin/ls")
Out[34]: 126584

In [35]: fs.statPath("/bin/ls")
Out[35]: os.stat_result(st_mode=33261, st_ino=75, st_dev=43, st_nlink=1, st_uid=0, st_gid=0, st_size=126584, st_atime=1455802667, st_mtime=1455802667, st_ctime=1462283990)
```

## Path Manipulation

You can do many path `isAbsolute`, `exists`, `statPath`, `getBaseName`, `getDirName`, `getParent`, `getFileExtension`, and `joinPaths`

```python
In [36]: path = "/bin/ls"

In [37]: fs.exists(path)
Out[37]: True

In [38]: fs.getBaseName(path)
Out[38]: 'ls'

In [39]: fs.getParent
fs.getParent

In [39]: fs.getParent(path)
Out[39]: '/bin'

In [40]: fs.getDirName(path)
Out[40]: '/bin/'

In [41]: fs.isAbsolute(path)
Out[41]: True
In [46]: fs.joinPaths("/bin", "ls")
Out[46]: '/bin/ls'

In [47]: path = "/home/nobody/script.py"
In [48]: fs.exists(path)
Out[48]: False
In [49]: fs.getFileExtension(path)
Out[49]: '.py'
In [8]: fs.getcwd()

Out[8]: '/'

In [9]: fs.changeDir("/tmp")
Out[9]: '/tmp'
```

## Higher level directory and files manipulation

You can manipulate (create, update, read, delete) files and directories easily with `j.sal.fs` via many useful functions like `fs.touch`, `fs.readFile`, `fs.writeFile`, `fs.md5sum`, `fs.copyFile`, `fs.moveFile`, `fs.list*` , `targzCompress`, `targzUncompress`, `gzip`, `gunzip`, `fs.removeIrreleventFiles`, `fs.remove`, and `fs.removeDirTree`:

```python
In [55]: mkdir testdir

In [56]: cd testdir/
/tmp/testdir

In [57]: ls

In [58]: fs.touch("file1.txt")

In [59]: ls
file1.txt

In [61]: fs.writeFile?
Signature: fs.writeFile(filename, contents, append=False)
Docstring:
Open a file and write file contents, close file afterwards
@param contents: string (file contents to be written)
File:      /opt/jumpscaleBETA8FIX/lib/JumpScale/sal/fs/SystemFS.py
Type:      method

In [62]: fs.writeFile("file1.txt", "this is a content")

In [63]: fs.readFile("file1.txt")
Out[63]: 'this is a content'

In [67]: fs.writeFile("file1.txt", "this is more content", append=True) #append mode

In [68]: fs.readFile("file1.txt")
Out[68]: 'this is a contentthis is more content'
In [69]: fs.md5sum("file1.txt")
Out[69]: 'c1afffed024c925366de6d8c088fb4a9'

In [70]: fs.copyFile("file1.txt", "file1copy.txt")
In [71]: fs.md5sum("file1copy.txt")
Out[71]: 'c1afffed024c925366de6d8c088fb4a9'

In [72]: !ls
file1.txt  file1copy.txt

In [73]: fs.moveFile("file1copy.txt", "file1moved.txt")

In [74]: !ls
file1.txt  file1moved.txt

In [75]: fs.remove("file1moved.txt")

In [76]: !ls
file1.txt
In [82]: list(map(fs.touch, [
'f1', 'f2', 'f3', 'f4']))
Out[82]: [None, None, None, None]

In [83]: !ls
f1  f2    f3  f4    file1.txt

In [84]: fs.writeFile("f1", "hello f1")

In [85]: fs.writeFile("f2", "hello f2")

In [86]: fs.writeFile("f3", "hello f3")

In [89]: fs.listFilesAndDirsInDir(".")
Out[89]: ['./f4', './f1', './file1.txt', './f2', './f3']

In [90]: cd ..
/tmp


In [92]: fs.targzCompress("testdir", "testdir.tar.gz")
In [93]: ls | grep testdir
testdir/
testdir.tar.gz
In [94]: fs.targzUncompress("testdir.tar.gz", "extracteddir.tar.gz")
[Thu09 10:42] - ...umpScale/sal/process/SystemProcess.py:1318 - INFO     - exec:tar xzf 'testdir.tar.gz' -C 'extracteddir.tar.gz'
[Thu09 10:42] - ...umpScale/sal/process/SystemProcess.py:1364 - INFO     - system.process.execute [tar xzf 'testdir.tar.gz' -C 'extracteddir.tar.gz']

In [95]: ls extracteddir.tar.gz/
f1  f2  f3  f4  file1.txt

In [96]: fs.readFile("extracteddir.tar.gz/f1")
Out[96]: 'hello f1'

In [100]: fs.gzip("testdir/file1.txt", "gzipped.gzip")

In [101]: ls | grep .gzip
gzipped.gzip

In [102]: fs.gunzip("gzipped.gzip", "unzipped")

In [103]: fs.readFile("unzipped")
Out[103]: 'this is a contentthis is more content'

In [113]: fs.listFilesInDir("tdirrenamed/")
Out[113]:
['tdirrenamed/p2.pyc',
 'tdirrenamed/p3.bak',
 'tdirrenamed/p3.py',
 'tdirrenamed/p2.bak',
 'tdirrenamed/p1.pyc']

In [5]: fs.removeIrrelevantFiles("/tmp/tdirrenamed/")
In [7]: fs.listFilesInDir("/tmp/tdirrenamed/")
Out[7]: ['/tmp/tdirrenamed/p3.py']
In [11]: fs.removeDirTree("extracteddir.tar.gz/") #removes everything recursively
In [13]: ls -al file1
-rw-r--r-- 1 root root 20 Jun  9 09:26 file1

In [15]: fs.chmod("file1", 0o444)

In [16]: ls -al file1
-r--r--r-- 1 root root 20 Jun  9 09:26 file1

In [17]: fs.chmod("file1", 0o777)

In [18]: ls -al file1
-rwxrwxrwx 1 root root 20 Jun  9 09:26 file1*
```

```
!!!
title = "FS"
date = "2017-04-08"
tags = []
```
