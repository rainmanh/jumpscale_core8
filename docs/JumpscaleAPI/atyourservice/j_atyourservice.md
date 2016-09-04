<!-- toc -->
## j.atyourservice

- /opt/jumpscale8/lib/JumpScale/baselib/atyourservice/AtYourServiceFactory.py
- Properties
    - debug
    - indocker
    - logger

### Methods

#### createAYSRepo(*path*) 

#### exist(*path*) 

```
Check if a repo at the given path exist or not, if multiple repos found under that path,
    an exception is raised

@param name: name of the repo
@type name: str

@returns:   True if exist, Flase if it doesnt, raises exception if mulitple found with the
    same name

```

#### existsTemplate(*name*) 

#### findAYSRepos(*path=''*) 

#### findTemplates(*name='', domain='', role=''*) 

#### get(*name='', path=''*) 

```
Get a repo by name or path, if repo does not exist, it will be created

@param name: Name of the repo to retrieve
@type name: str

@param path:    Path of the repo
@type path:     str

@return:    @AtYourServiceRepo object

```

#### getActionMethodDecorator() 

#### getActionsBaseClassMgmt() 

#### getActionsBaseClassNode() 

#### getBlueprint(*aysrepo, path*) 

#### getService(*key, die=True*) 

#### getTemplate(*name, die=True*) 

```
@param first means, will only return first found template instance

```

#### getTester(*name='fake_IT_env'*) 

#### reset() 

#### updateTemplates(*repos*) 

```
update the git repo that contains the service templates
args:
    repos : list of dict of repos to update, if empty, all repos are updated
            \{
                'url' : 'http://github.com/account/repo',
                'branch' : 'master'
            \}

```

