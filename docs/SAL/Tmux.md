# Tmux

```python
j.sal.tmux
```

## This library enables the user to do the followig:

- Create, kill and attach a Tmux session

```python
j.sal.tmux.createSession(sessionname, screens, user)
   # screens is a list with number of screens required in session and their names.
j.sal.tmux.killSession(sessionname, user)
j.sal.tmux.attachSession(sessionname, windowname, user)
```

- List all ongoing Tmux sessions

```python
j.sal.tmux.getSessions(user)
```

- Kill all ongoing Tmux sessions

```python
j.sal.tmux.killSessions(user):
```

- Create and kill a window inside a Tmux session

```python
j.sal.tmux.createWindow(session, name, user)
j.sal.tmux.killWindow(session, name, user)
```

- List all windows inside a Tmux session

```python
j.sal.tmux.getWindows(session, attemps, user):
```

- Check if a window with a certain name exists in a session

```python
j.sal.tmux.windowExists(session, name, user)
```

- Log a window to a file

```python
j.sal.tmux.logWindow(session, name, filename, user)
```

- Execute a certain command in a window inside a Tmux session

```python
j.sal.tmux.executeInScreen(sessionname, screenname, cmd, wait, cwd, env, user, tmuxuser)

  # cmd is the command to execute
  # wait is an int which indicates the time to wait for output (type = int)
  # workingdir is the working directory for command to be executed 
  # env a dictionary which states the environment variables for the command
```

- Attach to a session or a certain window inside a session

  ```python
  j.sal.tmux.attachSession(sessionname, windowname=None, user=None)
  ```

```
!!!
title = "Tmux"
date = "2017-04-08"
tags = []
```
