<!-- toc -->
## j.portal.tools.docpreprocessorparser

- /opt/jumpscale8/lib/JumpScale/portal/docpreprocessor/DocPreprocessorFactory.py

### Methods

#### generate(*preprocessorobject, outpath='out', startDoc='Home', visibility, reset=True, outputdocname='', format='preprocess', deepcopy*) 

#### generateFromDir(*path, macrosPaths, visibility, cacheDir=''*) 

```
@param path is starting point, will look for generate.cfg & params.cfg in this dir, input
    in these files will determine how preprocessor will work
@param macrosPaths are dirs where macro's are they are in form of tasklets
@param cacheDir if non std caching dir override here

```

#### get(*contentDirs, varsPath='', spacename=''*) 

```
@param contentDirs are the dirs where we will load wiki files from & parse

```

#### getMacroPath() 

