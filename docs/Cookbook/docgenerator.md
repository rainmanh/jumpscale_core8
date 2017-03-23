
# docgenerator

process all markdown files in a git repo, write a summary.md file
optionally call pdf gitbook generator to produce pdf(s)

# process

## arguments are

- outdirectory
- url of site where docs will be

## preprocess

- docgenerator walks over all directories below a dir
- docgenerator remembers when a .git repo & get's the url path
- docgenerator identifies following types of dirs
    - macros
        - each dir called macros is considered to be a macros dir
    - documentation
        - file ```.docs``` is in the root of such a dir
        - files in here can be definitions, documents, blogs, ...
        - config.yaml defines how to deal with the info in such a directory
    - the directories are remembered together with their git counterparts
- now all macro's are loaded
- now all filenames are remembered (this is to let the include work)

## process per doc directory (as found in previous step)

- walk over files in directory (recursive)
- when config.yaml overload previous one
- copy files to outdirectory
    - $outdir/$sitename/src
- walk over the files and for each file
    - make sure config.yaml as well as meta data info in file is loaded (is a big dict)
    - use mustache template engine to replace the arguments
    - execute the macro's & mustache again (recursive until no more macro's to be processed)
- per site do the production step
    - lookup template used, copy inside $outdir/$sitename
    - use hugo or ... to generate the site

# metadata

## config.yaml

- in root of each .docgenerator directory there can be a config.yaml
- depends (will fetch & process other mentioned locations, can be subsection of a repo or full branch)
- name is meaning full name of the Documentation part e.g js8_defs
- description e.g. definitions of jumpscale
```
name: js8_lots
depends:
    - https://github.com/Jumpscale/jumpscale_core8/tree/8.1.2/docs
    - https://github.com/Jumpscale/jscockpit
    - https://github.com/Jumpscale/ays_jumpscale8/tree/8.2.0
```
