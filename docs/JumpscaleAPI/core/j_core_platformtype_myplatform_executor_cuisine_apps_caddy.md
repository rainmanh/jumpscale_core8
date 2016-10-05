<!-- toc -->
## j.core.platformtype.myplatform.executor.cuisine.apps.caddy

- /opt/jumpscale8/lib/JumpScale/tools/cuisine/apps/CuisineCaddy.py

### Methods

#### caddyConfig(*sectionname, config*) 

```
config format see https://caddyserver.com/docs/caddyfile

```

#### install(*ssl, start=True, dns, reset*) 

```
Move binaries and required configs to assigned location.

@param ssl str:  this tells the firewall to allow port 443 as well as 80 and 22 to support
    ssl.
@param start bool: after installing the service this option is true will add the service
    to the default proccess manager an strart it .
@param dns str: default address to run caddy on.
@param reset bool:  if True this will install even if the service is already installed.

```

#### isInstalled() 

```
Checks if a package is installed or not
You can ovveride it to use another way for checking

```

#### start(*ssl*) 

