from JumpScale import j


class SerializerBase:

    def dump(self, filepath, obj):
        data = self.dumps(obj)
        j.sal.fs.writeFile(filepath, data)

    def load(self, filepath):
        b = j.sal.fs.fileGetContents(filepath)
        return self.loads(b)
