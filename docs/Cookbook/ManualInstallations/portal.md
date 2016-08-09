# Local Portal

- To install a portal we first need to have a cuisine connection.
- To get a local cuisine connection in a jsshell, do:

  ```
  executor = j.tools.executor.getLocal()
  cuisine = j.tools.cuisine.get(executor)
  ```

- To get a remote cuisine connection in a jsshell, do:

  ```
  executor = j.tools.executor.getSSHBased(addr, port, login, passwd, debug, checkok, allow_agent, look_for_keys, pushkey)
  cuisine = j.tools.cuisine.get(executor)
  ```

- Then do the portal installation in a jsshell, do:

  ```
  cuisine.portal.install()
  ```

This installs portal and all it's dependencies. It also runs the portal_start.py script by default. If you wish you can set the start flag = False to install without starting do this:

```
cuisine.portal.install(start=False)
```

- To start an already installed portal in a jsshell, do:

  ```
  cuisine.portal.start()
  ```

- To stop the running portal go to the tmux session on the machine running the portal script:

  ```
  tmux at -t portal
  ```

  and stop the running script

- To run the portal script again manually on the machine that has portal do:

  ```
  cd /opt/jumpscale8/apps/portals/example/ ;jspython portal_start.py
  ```
