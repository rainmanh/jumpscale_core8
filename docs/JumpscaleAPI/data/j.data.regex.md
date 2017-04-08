<!-- toc -->
## j.data.regex

- /opt/jumpscale8/lib/JumpScale/data/regex/RegexTools.py
- Properties
    - logger
    - templates

### Methods

#### extractBlocks(*text, blockStartPatterns=['.*'], blockStartPatternsNegative, blockStopPatterns, blockStopPatternsNegative, linesIncludePatterns=['.*'], linesExcludePatterns, includeMatchingLine=True*) 

```
look for blocks starting with line which matches one of patterns in blockStartPatterns and
    not matching one of patterns in blockStartPatternsNegative
block will stop when line found which matches one of patterns in blockStopPatterns and not
    in blockStopPatternsNegative or when next match for start is found
in block lines matching linesIncludePatterns will be kept and reverse for
    linesExcludePatterns
example pattern: '^class ' looks for class at beginning of line with space behind

```

#### extractFirstFoundBlock(*text, blockStartPatterns, blockStartPatternsNegative, blockStopPatterns, blockStopPatternsNegative, linesIncludePatterns=['.*'], linesExcludePatterns, includeMatchingLine=True*) 

#### findAll(*pattern, text, flags*) 

```
Search all matches of pattern in text and returns an array
@param pattern: Regex pattern to search for
@param text: Text to search in

```

#### findHtmlBlock(*subject, tofind, path, dieIfNotFound=True*) 

```
only find 1 block ideal to find e.g. body & header of html doc

```

#### findHtmlElement(*subject, tofind, path, dieIfNotFound=True*) 

#### findLine(*regex, text*) 

```
returns line when found
@param regex is what we are looking for
@param text, we are looking into

```

#### findOne(*pattern, text, flags*) 

```
Searches for a one match only on pattern inside text, will throw a RuntimeError if more
    than one match found
@param pattern: Regex pattern to search for
@param text: Text to search in

```

#### getINIAlikeVariableFromText(*variableName, text, isArray*) 

```
e.g. in text
'
test= something
testarray = 1,2,4,5
'
getINIAlikeVariable("test",text) will return 'something'
@isArray when True and , in result will make array out of
getINIAlikeVariable("testarray",text,True) will return [1,2,4,5]

```

#### getRegexMatch(*pattern, text, flags*) 

```
find the first match in the string that matches the pattern.
@return RegexMatch object, or None if didn't match any.

```

#### getRegexMatches(*pattern, text, flags*) 

```
match all occurences and find start and stop in text
return RegexMatches  (is array of RegexMatch)

```

#### match(*pattern, text*) 

```
search if there is at least 1 match

```

#### matchAllText(*pattern, text*) 

#### matchMultiple(*patterns, text*) 

```
see if any patterns matched
if patterns=[] then will return False

```

#### processLines(*text, includes='', excludes=''*) 

```
includes happens first
excludes last
both are arrays

```

#### removeLines(*pattern, text*) 

```
remove lines based on pattern

```

#### replace(*regexFind, regexFindsubsetToReplace, replaceWith, text*) 

```
Search for regexFind in text and if found, replace the subset regexFindsubsetToReplace of
    regexFind with replacewith and returns the new text
Example:
    replace("Q-Layer Server", "Server", "Computer", "This is a Q-Layer Server")
    will return "This is a Q-Layer Computer"
@param regexFind: String to search for, can be a regular expression
@param regexFindsubsetToReplace: The subset within regexFind that you want to replace
@param replacewith: The replacement
@param text: Text where you want to search and replace

```

#### replaceLines(*replaceFunction, arg, text, includes='', excludes=''*) 

```
includes happens first (includes of regexes eg @process.* matches full line starting with
    @process)
excludes last
both are arrays
replace the matched line with line being processed by the
    functionreplaceFunction(arg,lineWhichMatches)
the replace function has 2 params, argument & the matching line

```

#### yieldRegexMatches(*pattern, text, flags*) 

```
The same as getRegexMatches but instead of returning a list that contains all matches it
    uses yield to return a generator object
witch would improve the performance of the search function.

```


```
!!!
title = "J.data.regex"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.data.regex"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.data.regex"
date = "2017-04-08"
tags = []
```
