<!-- toc -->
## j.sal.fswalker

- /opt/jumpscale8/lib/JumpScale/sal/fs/SystemFSWalker.py

### Methods

#### find(*root, recursive=True, includeFolders, pathRegexIncludes=['.*'], pathRegexExcludes, contentRegexIncludes, contentRegexExcludes, depths*) 

#### walk(*root, callback, arg='', recursive=True, includeFolders, pathRegexIncludes=['.*'], pathRegexExcludes, contentRegexIncludes, contentRegexExcludes, depths, followlinks=True*) 

```
Walk through filesystem and execute a method per file

Walk through all files and folders starting at C\{root\}, recursive by
default, calling a given callback with a provided argument and file
path for every file we could find.

If C\{includeFolders\} is True, the callback will be called for every
folder we found as well.

Examples
========
>>> def my_print(arg, path):
...     print arg, path
...
>>> SystemFSWalker.walk('/foo', my_print, 'test:')
test: /foo/file1
test: /foo/file2
test: /foo/file3
test: /foo/bar/file4

return False if you want recursion to stop (means don't go deeper)

>>> def dirlister(arg, path):
...     print 'Found', path
...     arg.append(path)
...
>>> paths = list()
>>> SystemFSWalker.walk('/foo', dirlister, paths, recursive=False, includeFolders=True)
/foo/file1
/foo/file2
/foo/file3
/foo/bar
>>> print paths
['/foo/file1', '/foo/file2', '/foo/file3', '/foo/bar']

@param root: Filesystem root to crawl (string)
@param callback: Callable to call for every file found, func(arg, path) (callable)
@param arg: First argument to pass to callback
@param recursive: Walk recursive or not (bool)
@param includeFolders: Whether to call C\{callable\} for folders as well (bool)
@param pathRegexIncludes / Excludes  match paths to array of regex expressions
    (array(strings))
@param contentRegexIncludes / Excludes match content of files to array of regex
    expressions (array(strings))
@param depths array of depth values e.g. only return depth 0 & 1 (would mean first dir
    depth and then 1 more deep) (array(int))

```

#### walkFunctional(*root, callbackFunctionFile, callbackFunctionDir, arg='', callbackForMatchDir, callbackForMatchFile*) 

```
Walk through filesystem and execute a method per file and dirname

Walk through all files and folders starting at C\{root\}, recursive by
default, calling a given callback with a provided argument and file
path for every file & dir we could find.

To match the function use the callbackForMatch function which are separate for dir or file
when it returns True the path will be further processed
when None (function not given match will not be done)

Examples
========
>>> def my_print(path,arg):
...     print arg, path
...
#if return False for callbackFunctionDir then recurse will not happen for that dir

>>> def matchDirOrFile(path,arg):
...     return True #means will match all
...

>>> SystemFSWalker.walkFunctional('/foo', my_print,my_print,
    'test:',matchDirOrFile,matchDirOrFile)
test: /foo/file1
test: /foo/file2
test: /foo/file3
test: /foo/bar/file4

@param root: Filesystem root to crawl (string)
#TODO: complete

```


```
!!!
title = "J Sal Fswalker"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Sal Fswalker"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Sal Fswalker"
date = "2017-04-08"
tags = []
```
