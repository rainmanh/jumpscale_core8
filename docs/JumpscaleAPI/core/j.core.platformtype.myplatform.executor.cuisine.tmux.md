<!-- toc -->
## j.core.platformtype.myplatform.executor.cuisine.tmux

- /opt/jumpscale8/lib/JumpScale/tools/cuisine/CuisineTmux.py

### Methods

#### attachSession(*sessionname, windowname, user*) 

#### configure(*restartTmux, xonsh*) 

#### createSession(*sessionname, screens, user, killifexists=True, returnifexists=True*) 

```
@param name is name of session
@screens is list with nr of screens required in session and their names (is
    [$screenname,...])

```

#### createWindow(*session, name, user, cmd*) 

#### executeInScreen(*sessionname, screenname, cmd, wait=10, cwd, env, user='root', tmuxuser, reset, replaceArgs=True, resetAfter, die=True, async*) 

```
execute command in tmux & wait till error or till ok, default 10 sec
we will wait X seconds as specified in argument wait.

if async then we will wait 1 second to see if cmd got started succesfully and the exit
we do this by checking the error code after 1 second

@param sessionname Name of the tmux session
@param screenname Name of the window in the session
@param cmd command to execute
@param cwd workingdir for command only in new screen see newscr
@param env environment variables for cmd only in new screen see newscr (dict)
@param async, if async will fire & forget
@param resetAfter if True, will remove the tmux session after execution (error or not)

will return rc,out

```

#### getPid(*session, name, user*) 

#### getSessions(*user*) 

#### getWindows(*session, attemps=5, user*) 

#### killSession(*sessionname, user*) 

#### killSessions(*user*) 

#### killWindow(*session, name, user*) 

#### logWindow(*session, name, filename, user*) 

#### windowExists(*session, name, user*) 


```
!!!
title = "J.core.platformtype.myplatform.executor.cuisine.tmux"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.core.platformtype.myplatform.executor.cuisine.tmux"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.core.platformtype.myplatform.executor.cuisine.tmux"
date = "2017-04-08"
tags = []
```
