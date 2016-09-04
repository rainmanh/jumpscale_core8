<!-- toc -->
## j.data.text

- /opt/jumpscale8/lib/JumpScale/data/text/Text.py

### Methods

#### addCmd(*out, entity, cmd*) 

#### addTimeHR(*line, epoch, start=50*) 

#### addVal(*out, name, val, addtimehr*) 

#### ask(*content, name, args, ask=True*) 

```
look for @ASK statements in text, where found replace with input from user

syntax for ask is:
    @ASK name:aname type:str descr:adescr default:adefault regex:aregex retry:10
    minValue:10 maxValue:20 dropdownvals:1,2,3

    descr, default & regex can be between '' if spaces inside

    types are: str,float,int,bool,multiline,list

    retry means will keep on retrying x times until ask is done properly

    dropdownvals is comma separated list of values to ask for

@ASK can be at any position in the text

@return type,content

```

#### decodeUnicode2Asci(*text*) 

#### eval(*code*) 

```
look for \{\{\}\} in code and evaluate as python result is converted back to str

```

#### existsTemplateVars(*text*) 

```
return True if they exist

```

#### getBool(*text*) 

#### getDict(*text, ttype*) 

```
keys are always treated as string
@type can be int,bool or float (otherwise its always str)

```

#### getFloat(*text*) 

#### getInt(*text*) 

#### getList(*text, ttype='str'*) 

```
@type can be int,bool or float (otherwise its always str)

```

#### getMacroCandidates(*txt*) 

```
look for \{\{\}\} return as list

```

#### getTemplateVars(*text*) 

```
template vars are in form of $(something)
@return [("something1","$(Something)"),...

```

#### hrd2machinetext(*value, onlyone*) 

```
'something ' removes ''
all spaces & commas & : inside ' '  are converted
 SPACE -> \S
 " -> \Q
 , -> \K
 : -> \D
 \n -> \N

```

#### indent(*instr, nspaces=4, wrap=180, strip=True, indentchar=' '*) 

```
Indent a string a given number of spaces.

Parameters
----------

instr : basestring
    The string to be indented.
nspaces : int (default: 4)
    The number of spaces to be indented.

Returns
-------

str|unicode : string indented by ntabs and nspaces.

```

#### isFloat(*text*) 

#### isInt(*text*) 

#### isNumeric(*txt*) 

#### machinetext2str(*value*) 

```
       do reverse of:
            SPACE -> \S
            " -> \Q
            , -> \K
            : -> \D

-> \N

```

#### machinetext2val(*value*) 

```
do reverse of:
     SPACE -> \S
     " -> \Q
     , -> \K
     : -> \D
     \n -> return

```

#### prefix(*prefix, txt*) 

#### prefix_remove(*prefix, txt, onlyPrefix*) 

```
@param onlyPrefix if True means only when prefix found will be returned, rest discarded

```

#### prefix_remove_withtrailing(*prefix, txt, onlyPrefix*) 

```
there can be chars for prefix (e.g. '< :*: aline'  and this function looking for :*: would
    still work and ignore '< ')
@param onlyPrefix if True means only when prefix found will be returned, rest discarded

```

#### printCode(*code, style='vim'*) 

```
will use pygments to format code

```

#### pythonObjToStr(*obj, multiline=True, canBeDict=True, partial*) 

```
try to convert a python object to string representation works for None, bool, integer,
    float, dict, list

```

#### pythonObjToStr1line(*obj*) 

#### replaceQuotes(*value, replacewith*) 

#### replaceTemplateVars(*text, args*) 

```
@return changes,text
changes = \{key:newval, ...\}

```

#### sort(*txt*) 

```
removes all empty lines & does a sort

```

#### str2var(*string*) 

```
convert list, dict of strings
or convert 1 string to python objects

```

#### strip(*content*) 

#### stripItems(*line, items=['PATH', '"', ' ', "'", ':', '$\{PATH\}', '=', ',']*) 

#### toAscii(*value, maxlen*) 

#### toSafePath(*txt, maxlen*) 

```
process string so it can be used in a path on windows or linux

```

#### toStr(*value, codec='utf-8'*) 

#### toUnicode(*value, codec='utf-8'*) 

#### toolStripNonAsciFromText(*text*) 

#### wrap(*txt, length=80*) 

