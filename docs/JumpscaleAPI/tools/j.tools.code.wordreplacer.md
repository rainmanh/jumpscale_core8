<!-- toc -->
## j.tools.code.wordreplacer

- /opt/jumpscale8/lib/JumpScale/tools/codetools/WordReplacer.py
- Properties
    - synonyms

### Methods

#### removeConfluenceLinks(*text*) 

```
find [...] and remove the [ and the ]
TODO: 2  (id:19)

```

#### replace(*text*) 

#### replaceInConfluence(*text*) 

```
@[..|.] will also be looked for and replaced

```

#### reset() 

#### synonymAdd(*name='', simpleSearch='', regexFind='', regexFindForReplace='', replaceWith='', replaceExclude='', addConfluenceLinkTags*) 

```
Adds a new synonym to this replacer
@param name: Synonym name
@param simpleSearch: Search text for sysnonym, if you supply this, then the synonym will
    automatically generate a matching regex pattern that'll be used to search for this
    string, if you want to specificy the regex explicitly then use regexFind instead.
@param regexFind: Provide this regex only if you didn't provide simpleSearch, it
    represents the regex that'll be used in search for this synonym . It overrides the
    default synonym search pattern
@param regexFindForReplace: The subset within regexFind that'll be replaced for this
    synonym

```

#### synonymsAddFromFile(*path, addConfluenceLinkTags*) 

```
load synonym satements from a file in the following format
[searchStatement]:[replaceto]
or
'[regexFind]':'[regexReplace]':replaceto
note: delimiter is :
note: '' around regex statements
e.g.
******
master?daemon:ApplicationServer
application?server:ApplicationServer
'application[ -_]+server':'application[ -_]+server':ApplicationServer
'\[application[ -_]+server\]':'application[ -_]+server':ApplicationServer
******
@param addConfluenceLinkTags id True then replaced items will be surrounded by []
    (Boolean)

```

#### synonymsPrint() 


```
!!!
title = "J.tools.code.wordreplacer"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.tools.code.wordreplacer"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.tools.code.wordreplacer"
date = "2017-04-08"
tags = []
```
