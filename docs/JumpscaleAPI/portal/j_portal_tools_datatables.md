<!-- toc -->
## j.portal.tools.datatables

- /opt/jumpscale8/lib/JumpScale/portal/datatables/DataTables.py
- Properties
    - cache
    - inited

### Methods

#### executeMacro(*row, field*) 

#### getClient(*namespace, category*) 

#### getData(*namespace, category, key, **kwargs*) 

#### getFromCache(*key*) 

#### getTableDefFromActorModel(*appname, actorname, modelname, excludes*) 

```
@return fields : array where int of each col shows position in the listProps e.g. [3,4]
      means only col 3 & 4 from listprops are levant, you can also use it to define the
    order
      there can be special columns added which are wiki templates to form e.g. an url or
    call a macro, formatted as a string
      e.g. [3,4,"\{\{amacro: name:$3 descr:$4\}\}","[$1|$3]"]
@return fieldids: ids to be used for the fields ["name","descr","remarks","link"]
@return fieldnames: names to be used for the fields
    ["Name","Description","Remarks","Link"], can be manipulated for e.g. translation

```

#### storInCache(***kwargs*) 

