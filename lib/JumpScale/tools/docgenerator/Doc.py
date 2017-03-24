from JumpScale import j
import toml
import pystache


class Doc:
    """
    """

    def __init__(self, path, name, docSource):
        self.path = path
        self.name = name
        self.docSource = docSource
        self.rpath = j.sal.fs.pathRemoveDirPart(path, self.docSource.path)
        self.content = None
        self._processStep1Done = False

    def processYamlData(self, dataText):
        try:
            data = j.data.serializer.yaml.loads(dataText)
        except Exception as e:
            from IPython import embed
            print("DEBUG NOW yaml load issue in doc")
            embed()
            raise RuntimeError("stop debug here")
        self.data.update(data)

    def processContent(self):

        content = self.content

        regex = "\$\{+\w+\(.*\)\}"
        for match in j.data.regex.yieldRegexMatches(regex, content, flags=0):
            methodcode = match.founditem.strip("${}")
            methodcode = methodcode.replace("(", "(self,")

            # find level we are in
            self.last_level = 0
            for line in content.split("\n"):
                if line.find(match.founditem) != -1:
                    # we found position where we are working
                    break
                if line.startswith("#"):
                    self.last_level = len(line.split(" ", 1)[c0].strip())
            try:
                result = eval("j.tools.docgenerator.macros." + methodcode)
            except Exception as e:
                raise e

            # replace return of function
            content = content.replace(match.founditem, result)

        # lets rewrite our style args to mustache style, so we can use both
        regex = "\$\{[a-zA-Z!.]+}"
        for match in j.data.regex.yieldRegexMatches(regex, content, flags=0):
            methodcode = match.founditem.strip("${}").replace(".", "_")
            content = content.replace(match.founditem, "{{%s}}" % methodcode)

        # process multi line blocks
        state = "start"
        block = ""
        out = ""
        for line in content.split("\n"):
            if state == "blockstart" and (line.startswith("```") or line.startswith("'''")):
                # end of block
                line0 = block.split("\n")[0]
                block = "\n".join(block.split("\n")[1:])
                if line0.startswith("!!!"):
                    methodcode = line0[3:]
                    methodcode = methodcode.rstrip(", )")  # remove end )
                    methodcode = methodcode.replace("(", "(self,")
                    if not methodcode.strip() == line0[3:].strip():
                        # means there are parameters
                        methodcode += ",content=block)"
                    else:
                        methodcode += "(content=block)"
                    methodcode = methodcode.replace(",,", ",")

                    print("methodcode:'%s'" % methodcode)
                    if line0[3:].strip().strip(".").strip(",") == "":
                        self.processYamlData(block)
                        block = ""
                    else:
                        cmd = "j.tools.docgenerator.macros." + methodcode
                        print(cmd)
                        try:
                            block = eval(cmd)
                        except Exception as e:
                            from IPython import embed
                            print("DEBUG NOW 88")
                            embed()
                            raise RuntimeError("stop debug here")
                            raise e
                else:
                    block = "'''\n%s\n'''\n" % block
                out += block
                block = ""
                state = "start"
                continue

            if state == "blockstart":
                block += "%s\n" % line
                continue

            if state == "start" and (line.startswith("```") or line.startswith("'''")):
                state = "blockstart"
                continue

            out += "%s\n" % line

        content = out

        self.content = pystache.render(content, self.data)

    def process(self):
        if self.docSource.defaultContent != "":
            content = self.docSource.defaultContent
            if content[-1] != "\n":
                content += "\n"
        else:
            content = ""
        self.content = content
        self.content += j.sal.fs.fileGetContents(self.path)

        for i in range(3):
            self.processContent()  # dirty hack to do iterative behaviour for processing macro's

    def write(self, docSite):

        C = "+++\n"
        C += toml.dumps(self.data)
        C += "\n+++\n\n"

        # C+=

        C += self.content

        dpath = j.sal.fs.joinPaths(docSite.outpath, "src", self.rpath)
        j.sal.fs.createDir(j.sal.fs.getDirName(dpath))
        j.sal.fs.writeFile(filename=dpath, contents=C)

        # self.last_content = content
        # self.last_path = self.path
        # self.last_dest = j.sal.fs.joinPaths(j.sal.fs.getDirName(path), j.sal.fs.getBaseName(path)[1:])
        # self.last_dest=j.sal.fs.joinPaths(self.root,j.sal.fs.pathRemoveDirPart(path,self.source))
        # j.sal.fs.createDir(j.sal.fs.getDirName(self.last_dest))
        # j.data.regex.replace(regexFind, regexFindsubsetToReplace, replaceWith, text)

    def __repr__(self):
        return "doc:%s:%s" % (self.name, self.path)

    __str__ = __repr__
