# Best Practices

## Editor

- atom is a very nice editor
- best to install following python helpers

```
pip3 install jedi
pip3 install autopep8
pip3 install flake8
pip3 install flake8-docstrings
```

- must have extension
  - Python Autopep8
  - Python Tools
  - Python Indent
  - Linter Python Pep8
  - Linter Flake8
  - Autocomplete Python
  - Git Time Machine

- if you work with markdown

  - Markdown Mindmap
  - Markdown Scroll Sync
  - Linter Markdown
  - Markdown Pdf
  - Markdown Toc
  - Markdown Folder
  - Language Markdown
  - Tool Bar Markdown Writer

- if you work with raml (API definition format)

  - Api Workbench

open snippets.cson (under file)
and add

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
