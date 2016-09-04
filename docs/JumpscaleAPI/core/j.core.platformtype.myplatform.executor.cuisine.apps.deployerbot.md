<!-- toc -->
## j.core.platformtype.myplatform.executor.cuisine.apps.deployerbot

- /opt/jumpscale8/lib/JumpScale/tools/cuisine/apps/CuisineDeployerBot.py
- Properties
    - cuisine

### Methods

#### create_config(*token, g8_addresses, dns, oauth*) 

```
token: telegram bot token received from @botfather
g8_addresses: list of g8 addresses. e.g: ['be-scale-1.demo.greenitglobe.com', 'du-
    conv-2.demo.greenitglobe.com']
dns: dict containing login and password e.g: \{'login': 'admin', 'password':'secret'\}
oauth: dict containing
       host
       oauth
       client_id
       client_secret
       itsyouonline.host
see https://github.com/Jumpscale/jscockpit/blob/master/deploy_bot/README.md for example

```

#### install(*start=True, token, g8_addresses, dns, oauth*) 

```
Install deployerbot
If start is True, token g8_addresses, dns and oauth should be specified

```

#### install_deps(**) 

#### isInstalled(**) 

```
Checks if a package is installed or not
You can ovveride it to use another way for checking

```

#### link_code(**) 

#### start(*token, g8_addresses, dns, oauth*) 

```
token: telegram bot token received from @botfather
g8_addresses: list of g8 addresses. e.g: ['be-scale-1.demo.greenitglobe.com', 'du-
    conv-2.demo.greenitglobe.com']
dns: dict containing login and password e.g: \{'login': 'admin', 'password':'secret'\}
oauth: dict containing
       host
       oauth
       client_id
       client_secret
       itsyouonline.host
see https://github.com/Jumpscale/jscockpit/blob/master/deploy_bot/README.md for example

```

