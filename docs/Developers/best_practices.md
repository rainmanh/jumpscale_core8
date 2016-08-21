# Best Practices

## put todo's in code

format
```
#TODO: *1 some to do text ..
```

- ```#``` is optional
- ```*1 *2 *3 ``` are priorities *1 = highest, means do in current sprint
- TODO: needs to be capital !

### find the todo's

- select regex
- make sure you only search in *.py

![](search_atom.png)

there is a nice plugin for atom to show the todo's

## Editor

- atom is a very nice editor
- best to install following python helpers

```bash
#pip3 install jedi
pip3 install autopep8
pip3 install flake8
pip3 install flake8-docstrings
```



- if you work with raml (API definition format)

  - Api Workbench

open snippets.cson (under file) and add

```json
'.source.python':
  'ipshell':
    'prefix': 'ipshell'
    'body': """
        from IPython import embed
        print ("DEBUG NOW $1")
        embed()
        raise RuntimeError(\"stop debug here\")
        """
  'debug':
    'prefix': 'debug'
    'body': """
        from pudb import set_trace; set_trace()
        """
```
## Autoformat markdown docs

```
j.tools.markdown.tidy(path="")
```

## Auto Pep8 code

e.g.

```
autopep8 -r --max-line-length 120  -i /Users/despiegk/opt/code/github/jumpscale/jumpscale_core8/lib/JumpScale/
```

- -i means replace file
- -r recursive

## Path manipulation

- Please no longer use `j.system.fs`, use `j.tools.path.get(...` check out doc to returned path object
- Please no longer use the different fs walker functions/classes under `j.system`, the `j.tools.path` has a walkerfunction build in
