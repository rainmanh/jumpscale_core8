from JumpScale import j

class SerializerBase(object):

    def dump(self,filepath,obj):
        data=self.dumps(obj)
        j.do.writeFile(filepath,data)

    def load(self,filepath):
        b=j.do.readFile(filepath)
        return self.loads(b)
