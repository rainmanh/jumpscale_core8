## HRD Schema

- defines the format of an HRD
- each item of the Schema is an HRD Type (is a separate line)

format
```
aname = type:str descr:adescr default:adefault regex:aregex minValue:10 maxValue:20 multichoice:'1,2,3' list
```

- descr
    - default & regex can be between '' if spaces inside
- Types
    - are: str,multiline,float,int,bool,date,email,tel,ipaddr,float
- Multichoice
    - is comma separated list of values to ask for
- List
    - is a label
- min-maxValue
    - only relevant for int's 
- default
    - default value

### How To Process

```

```