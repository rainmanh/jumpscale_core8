<!-- toc -->
## j.core.platformtype.myplatform.executor.cuisine.group

- /opt/jumpscale8/lib/JumpScale/tools/cuisine/CuisineGroup.py

### Methods

#### check(*name*) 

```
Checks if there is a group defined with the given name,
returning its information as:
'\{"name":<str>,"gid":<str>,"members":<list[str]>\}'
or
'\{"name":<str>,"gid":<str>\}' if the group has no members
or
'None' if the group does not exists.

```

#### create(*name, gid*) 

```
Creates a group with the given name, and optionally given gid.

```

#### ensure(*name, gid*) 

```
Ensures that the group with the given name (and optional gid)
exists.

```

#### remove(*group, wipe*) 

```
Removes the given group, this implies to take members out the group
if there are any.  If wipe=True and the group is a primary one,
deletes its user as well.

```

#### user_add(*group, user*) 

```
Adds the given user/list of users to the given group/groups.

```

#### user_check(*group, user*) 

```
Checks if the given user is a member of the given group. It
will return 'False' if the group does not exist.

```

#### user_del(*group, user*) 

```
remove the given user from the given group.

```

#### user_ensure(*group, user*) 

```
Ensure that a given user is a member of a given group.

```


```
!!!
title = "J Core Platformtype Myplatform Executor Cuisine Group"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Core Platformtype Myplatform Executor Cuisine Group"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Core Platformtype Myplatform Executor Cuisine Group"
date = "2017-04-08"
tags = []
```
