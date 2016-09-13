# JSModels

These are easy to use models which can be cached in redis & stored to mongodb.

## create a model

```python
from mongoengine.fields import *
from mongoengine import DoesNotExist, EmbeddedDocument, Document

ModelBase=j.data.models.getModelBaseClass()

class Repository(ModelBase, Document):
    nr = IntField(required=True)
    name = StringField(default='')

j.data.models.addModel("github",Repository,redis=j.core.db)

#now we can use the model as follows

repoEmptyObj=j.data.models.github.Repository()
repoEmptyObj.nr=1
repoEmptyObj.name="test"

repoEmptyObj.save()

repoEmptyObj2=j.data.models.github.Repository()
repoEmptyObj2.nr=2
repoEmptyObj2.name="test2"
repoEmptyObj2.save()

print (repoEmptyObj2)

def findall(obj):
    return True

print(repoEmptyObj2.findByMethod(findall))

print(repoEmptyObj2.hash)
```

# #
