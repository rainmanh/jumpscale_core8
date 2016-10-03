<!-- toc -->
## j.data.serializer.serializers

- /opt/jumpscale8/lib/JumpScale/data/serializers/SerializersFactory.py
- Properties
    - yaml
    - json
    - base64
    - int
    - types
    - dict
    - time
    - toml
    - hrd
    - blowfish

### Methods

#### get(*serializationstr, key=''*) 

```
serializationstr FORMATS SUPPORTED FOR NOW
    m=MESSAGEPACK
    c=COMPRESSION WITH BLOSC
    b=blowfish
    s=snappy
    j=json
    b=base64
    l=lzma
    p=pickle
    r=bin (means is not object (r=raw))
    l=log
    d=dict (check if there is a dict to object, if yes use that dict, removes the private
    properties (starting with _))

 example serializationstr "mcb" would mean first use messagepack serialization then
    compress using blosc then encrypt (key will be used)

this method returns

```

#### getBlosc() 

#### getMessagePack() 

#### getSerializerType(*type, key=''*) 

```
serializationstr FORMATS SUPPORTED FOR NOW
    m=MESSAGEPACK
    c=COMPRESSION WITH BLOSC
    b=blowfish
    s=snappy
    j=json
    6=base64
    l=lzma
    p=pickle
    r=bin (means is not object (r=raw))
    l=log

```

