<!-- toc -->
## j.tools.code

- /opt/jumpscale8/lib/JumpScale/tools/codetools/CodeTools.py

### Methods

#### classEditGeany(*classs*) 

```
look for editor (uses geany) and then edit the file

```

#### classEditWing(*classs*) 

```
look for editor (uses geany) and then edit the file

```

#### classGetBase() 

#### classGetJSModelBase() 

#### classGetJSRootModelBase() 

#### classInfoGet(*classs*) 

```
returns filepath,linenr,sourcecode

```

#### classInfoPrint(*classs*) 

```
print info like source code of class

```

#### deIndent(*content, level=1*) 

#### dict2JSModelobject(*obj, data*) 

#### dict2object(*obj, data*) 

#### indent(*content, level=1*) 

#### object2dict(*obj, dieOnUnknown, ignoreKeys, ignoreUnderscoreKeys*) 

#### object2dict4index(*obj*) 

```
convert object to a dict
only properties on first level are considered
and properties of basic types like int,str,float,bool,dict,list
ideal to index the basics of an object

```

#### object2json(*obj, pretty, skiperrors, ignoreKeys, ignoreUnderscoreKeys*) 

#### object2yaml(*obj*) 

#### pprint(*obj*) 

#### textToTitle(*text, maxnrchars=60*) 

```
try to create a title out of text, ignoring irrelevant words and making lower case and
    removing
not needed chars

```

