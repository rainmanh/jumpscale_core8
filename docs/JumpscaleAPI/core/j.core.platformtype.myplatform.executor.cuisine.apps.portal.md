<!-- toc -->
## j.core.platformtype.myplatform.executor.cuisine.apps.portal

- /opt/jumpscale8/lib/JumpScale/tools/cuisine/apps/CuisinePortal.py
- Properties
    - main_portal_dir
    - portal_dir

### Methods

#### addSpace(*spacepath*) 

#### addactor(*actorpath*) 

#### getcode() 

#### install(*start=True, mongodbip='127.0.0.1', mongoport=27017, influxip='127.0.0.1', influxport=8086, grafanaip='127.0.0.1', grafanaport=3000, login='', passwd=''*) 

#### installDeps() 

```
make sure new env arguments are understood on platform

```

#### linkCode() 

#### serviceconnect(*mongodbip='127.0.0.1', mongoport=27017, influxip='127.0.0.1', influxport=8086, grafanaip='127.0.0.1', grafanaport=3000*) 

#### set_admin_password(*passwd*) 

#### start(*passwd*) 

```
Start the portal
passwd : if not None, change the admin password to passwd after start

```

#### stop() 

