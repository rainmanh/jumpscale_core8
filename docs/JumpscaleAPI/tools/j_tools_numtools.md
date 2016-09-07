<!-- toc -->
## j.tools.numtools

- /opt/jumpscale8/lib/JumpScale/tools/numtools/NumTools.py
- Properties
    - currencies

### Methods

#### collapseDictOfArraysOfFloats(*dictOfArrays*) 

```
format input \{key:[,,,]\}

```

#### collapseDictOfDictOfArraysOfFloats(*data*) 

```
format input \{key:\{key:[,,,]\},key:\{key:[,,,]\},...\}

```

#### getMonthsArrayForXYear(*X, initvalue*) 

```
return array which represents all months of X year, each value = None

```

#### getYearAndMonthFromMonthId(*monthid, startyear*) 

```
@param monthid is an int representing a month over a period of time e.g. month 24, is the
    24th moth
@return returns year e.g. 1999 and month in the year

```

#### interpolateList(*tointerpolate, left, right, floatnr*) 

```
interpolates a list (array)
if will fill in the missing information of an array
each None value in array will be interpolated

```

#### roundDown(*value, floatnr*) 

#### roundUp(*value, floatnr*) 

#### setMinValueInArray(*array, minval*) 

#### text2val(*value*) 

```
value can be 10%,0.1,100,1m,1k  m=million
USD/EUR/CH/EGP/GBP are also understood
all gets translated to eur
e.g.: 10%
e.g.: 10EUR or 10 EUR (spaces are stripped)
e.g.: 0.1mEUR or 0.1m EUR or 100k EUR or 100000 EUR

```

