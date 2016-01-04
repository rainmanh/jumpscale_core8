from JumpScale import j

CATEGORY = "ays:bp"


def log(msg, level=2):
    j.logger.log(msg, level=level, category=CATEGORY)


class Blueprint(object):
    """
    """

    def __init__(self, path):
        self.model=j.data.serializer.yaml.loads(j.sal.fs.fileGetContents(path))

        self.process()

    def process(self):
        for key,item in self.model.items():
            aysname,aysinstance=key.split("_",1)
            r=j.atyourservice.getRecipe(name=aysname)
            r.newInstance(instance=aysinstance,args=item)
