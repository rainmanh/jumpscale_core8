<!-- toc -->
## j.tools.docgenerator

- /opt/jumpscale8/lib/JumpScale/tools/docgenerator/DocGenerator.py

### Methods

process all markdown files in a git repo, write a summary.md file
optionally call pdf gitbook generator to produce a pdf

#### get(*source='', pdfpath='', macrosPath=''*) 

```
will look for config.yaml in $source/config.yaml

@param source is the location where the markdown docs are which need to be processed
    if not specified then will look for root of git repo and add docs
    source = $gitrepoRootDir/docs

@param pdfpath if specified will generate a pdf using the gitbook tools (needs to be
    installed)
    if pdfpath=="auto" then put $reponame.pdf in $dest dir

@param macropath if "" then will look for subdir macro from source dir

```

