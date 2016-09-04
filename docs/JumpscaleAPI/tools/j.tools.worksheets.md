<!-- toc -->
## j.tools.worksheets

- /opt/jumpscale8/lib/JumpScale/tools/worksheets/Sheets.py
- Properties
    - sheetsByCategory
    - sheetNames
    - sheets

### Methods

#### add(*sheet, category*) 

#### aggregateSheets(*sheetnames, rowdescr, category, aggregateSheetName='Total', aggregation*) 

```
@param sheetnames are the sheets to aggregate
@param rowdescr \{groupname:[rownames,...]\}

```

#### applyFunction(*rows, method, rowDest, params*) 

```
@param rows is array if of rows we would like to use as inputvalues
@param rowDest if empty will be same as first row
@param method is python function with params (values,params) values are inputvalues from
    the rows

```

#### dict2obj(*data*) 

#### dict2sheet(*data*) 

#### multiplyRows(*rows, newRow*) 

#### new(*name, nrcols=72, headers, category*) 

#### obj2dict(**) 

#### sumRows(*rows, newRow*) 

```
make sum of rows
@param rows is list of rows to add
@param newRow is the row where the result will be stored

```

