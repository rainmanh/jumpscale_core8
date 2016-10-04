<!-- toc -->
## j.data.tags

- /opt/jumpscale8/lib/JumpScale/data/tags/TagsFactory.py

### Methods

Factory Class of dealing with TAGS     

#### getObject(*tagstring='', setFunction4Tagstring*) 

```
check whether labelname exists in the labels

@param tagstring:  example "important customer:kristof"
@type tagstring: string

```

#### getTagString(*labels, tags*) 

```
Return a valid tags string, it's recommended to use this function
and not to build the script manually to skip reserved letters.

@param labels: A set of labels
@param tags: A dict with key values

```

