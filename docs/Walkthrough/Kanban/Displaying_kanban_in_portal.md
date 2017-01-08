## Displaying kanban in portal 

The data retrived from gogs in the [Migrating Data Models](Walkthrough/Models/Migrating_data_from_gogs.md)
can now be displayed using a macro in portal that allows filtering within the wiki itself.

The macro is called kanbandata which allows us to take input specific issues, lables, user and others to filter on.  
This is demonstarted bellow, in the example wiki :
 - The first paramter specifies which source of data to get from in this case `issues`
 - The second parameter specifies the lables to filter  issues on so in this case `priority_critical`, and  `state_verification`
 - the third paramter specifies to also filter issues  on assigned user with id `1` names wer avoided as gogs allows un duplication of usernames.
```
{{kanbandata:issue label:priority_critical,state_verification assingee:1 }}
```



