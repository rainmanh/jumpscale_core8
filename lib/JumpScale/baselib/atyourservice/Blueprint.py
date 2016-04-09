from JumpScale import j


class Blueprint(object):
    """
    """

    def __init__(self, path):
        self.logger = j.logger.get('j.atyourservice.blueprint')
        self.path=path
        self.models=[]
        self._contentblocks=[]
        content=""
        content0=j.sal.fs.fileGetContents(path)
        nr=0
        #we need to do all this work because the yaml parsing does not maintain order because its a dict
        for line in content0.split("\n"):
            if len(line)>0 and line[0]=="#":
                continue
            if content=="" and line.strip()=="":
                continue

            line=line.replace("\t","    ")
            nr+=1
            if len(content)>0 and (len(line)>0 and line[0]!=" "):
                self._add2models(content,nr)
                content=""

            content+="%s\n"%line

        self._add2models(content,nr)
        self._contentblocks=[]

        self.content=content0

    def loadrecipes(self):
        for model in self.models:
            if model!=None:
                for key,item in model.items():
                    aysname,aysinstance=key.split("__",1)
                    if not aysname.startswith('blueprint.'):
                        blueaysname = 'blueprint.%s' % aysname
                        try:
                            j.atyourservice.getRecipe(name=blueaysname)
                            continue
                        except j.exceptions.Input:
                            pass
                    try:
                        j.atyourservice.getRecipe(name=aysname)
                    except Exception as e:
                        e.source=" Try to load recipe for %s in blueprint %s."%(key,self.path)
                        raise e

                        

    def execute(self):
        for model in self.models:
            if model is not None:
                for key, item in model.items():
                    self.logger.debug("blueprint model execute:%s %s"%(key,item))
                    aysname, aysinstance = key.split("__", 1)
                    if not aysname.startswith('blueprint.'):
                        blueaysname = 'blueprint.%s' % aysname
                        try:
                            r = j.atyourservice.getRecipe(name=blueaysname)
                        except j.exceptions.Input:
                            r = j.atyourservice.getRecipe(name=aysname)
                    yaml=model[key]
                    aysi=r.newInstance(instance=aysinstance, args=item, yaml=yaml)
                    aysi.init()

    def _add2models(self,content,nr):
        #make sure we don't process double
        if content in self._contentblocks:
            return
        self._contentblocks.append(content)
        try:
            model=j.data.serializer.yaml.loads(content)
        except Exception as e:
            msg="Could not process blueprint: '%s', line: '%s', content '%s'\nerror:%s"%(self.path,nr,content,e)
            raise j.exceptions.RuntimeError(msg)

        self.models.append(model)

    def __str__(self):
        return str(self.content)

    __repr__=__str__
