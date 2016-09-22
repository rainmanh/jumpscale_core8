The JS models are very simple to use Each model defines a schema for a collection of objects of the same type to be stored and retrieved from the MongoDB JS already has a ModelBase which takes care of all logic

- To create a model: ``` from mongoengine import Document from JumpScale.data.models.Models import ModelBase

class TestDemo(ModelBase, Document): name = StringField(default='master')

```

* To create a namespace, just make sure you inherit from NameSpaceLoader
This can be done by:
```

from JumpScale.data.models.BaseModelFactory import NameSpaceLoader

class MyNameSpace(NameSpaceLoader): def **init**(self): self.**jslocation** = "j.data.models.mynamespace" super(MyNameSpace, self).**init**(Models) # Where models are your own defined models

```

* To create generic DemoData:
```

from JumpScale.data.models.DemoData import create, load create(outputpath)

```

* To load user-defined data into your db:
```

load(path=path_to_your_json_objects) ```
