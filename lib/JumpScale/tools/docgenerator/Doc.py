from JumpScale import j
import toml
import pystache
import copy


class Doc:
    """
    """

    def __init__(self, path, name, docSite):
        self.path = path
        self.name = name
        self.docSite = docSite
        self.rpath = j.sal.fs.pathRemoveDirPart(path, self.docSite.path).strip("/")
        self.content = None
        self._defContent = ""
        self.data = {}
        self.show = True

        if j.sal.fs.getDirName(self.path).strip("/").split("/")[-1][0] == "_":
            # means the subdir starts with _
            self.show = False

    def _processData(self, dataText):
        try:
            data = j.data.serializer.toml.loads(dataText)
        except Exception as e:
            from IPython import embed
            print("DEBUG NOW toml load issue in doc")
            embed()
            raise RuntimeError("stop debug here")
        self._updateData(data)

    def _updateData(self, data):
        res = {}
        for key, val in self.data.items():
            if key in data:
                valUpdate = copy.copy(data[key])
                if j.data.types.list.check(val):
                    if not j.data.types.list.check(valUpdate):
                        raise j.exceptions.Input(
                            message="(%s)\nerror in data structure, list should match list" % self, level=1, source="", tags="", msgpub="")
                    for item in valUpdate:
                        if item not in val and item != "":
                            val.append(item)
                    self.data[key] = val
                else:
                    self.data[key] = valUpdate
        for key, valUpdate2 in data.items():
            # check for the keys not in the self.data yet and add them, the others are done above
            if key not in self.data:
                self.data[key] = copy.copy(valUpdate2)  # needs to be copy.copy otherwise we rewrite source later

    @property
    def defaultContent(self):
        if self._defContent == "":
            keys = [item for item in self.docSite.defaultContent.keys()]
            keys.sort(key=len)
            C = ""
            for key in keys:
                key = key.strip("/")
                if self.rpath.startswith(key):
                    C2 = self.docSite.defaultContent[key]
                    if len(C2) > 0 and C2[-1] != "\n":
                        C2 += "\n"
                    C += C2
            self._defContent = C
        return self._defContent

    def processDefaultData(self):
        """
        empty data, go over default data's and update in self.data
        """
        self.data = {}
        keys = [item for item in self.docSite.defaultData.keys()]
        keys.sort(key=len)
        for key in keys:
            key = key.strip("/")
            if self.rpath.startswith(key):
                data = self.docSite.defaultData[key]
                self._updateData(data)

    @property
    def url(self):
        rpath = j.sal.fs.pathRemoveDirPart(self.path, self.docSite.path)
        rpath = rpath[:-3]
        rpath += '/'
        return "%s%s" % (self.docSite.sitepath, rpath)

    def processContent(self):
        content = self.content

        # regex = "\$\{+\w+\(.*\)\}"
        # for match in j.data.regex.yieldRegexMatches(regex, content, flags=0):
        #     methodcode = match.founditem.strip("${}")
        #     methodcode = methodcode.replace("(", "(self,")
        #
        #     # find level we are in
        #     self.last_level = 0
        #     for line in content.split("\n"):
        #         if line.find(match.founditem) != -1:
        #             # we found position where we are working
        #             break
        #         if line.startswith("#"):
        #             self.last_level = len(line.split(" ", 1)[c0].strip())
        #     try:
        #         result = eval("j.tools.docgenerator.macros." + methodcode)
        #     except Exception as e:
        #         raise e
        #
        #     # replace return of function
        #     content = content.replace(match.founditem, result)
        #
        # # lets rewrite our style args to mustache style, so we can use both
        # regex = "\$\{[a-zA-Z!.]+}"
        # for match in j.data.regex.yieldRegexMatches(regex, content, flags=0):
        #     methodcode = match.founditem.strip("${}").replace(".", "_")
        #     content = content.replace(match.founditem, "{{%s}}" % methodcode)

        ws = j.tools.docgenerator.webserver + self.docSite.name

        regex = "\] *\([a-zA-Z0-9\.\-\_\ \/]+\)"  # find all possible images
        for match in j.data.regex.yieldRegexMatches(regex, content, flags=0):
            # print("##:%s" % match)
            fname = match.founditem.strip("[]").strip("()")
            if match.founditem.find("/") != -1:
                fname = fname.split("/")[1]
            if j.sal.fs.getFileExtension(fname).lower() in ["png", "jpg", "jpeg", "mov", "mp4"]:
                fnameFound = self.docSite.getFile(fname, die=True)
                # if fnameFound==None:
                #     torepl="ERROR:"
                content = content.replace(match.founditem, "](/%s/files/%s)" % (self.docSite.name, fnameFound))
            elif j.sal.fs.getFileExtension(fname).lower() in ["md"]:
                shortname = fname.lower()[:-3]
                if shortname not in self.docSite.docs:
                    raise j.exceptions.Input(message="Could not find link '%s' in %s" %
                                             (fname, self), level=1, source="", tags="", msgpub="")
                thisdoc = self.docSite.docs[shortname]
                content = content.replace(match.founditem, "](%s)" % (thisdoc.url))

        regex = "src *= *\" */?static"
        for match in j.data.regex.yieldRegexMatches(regex, content, flags=0):
            content = content.replace(match.founditem, "src = \"/")

        # process multi line blocks
        state = "start"
        block = ""
        out = ""
        codeblocks = []
        for line in content.split("\n"):
            if state == "blockstart" and (line.startswith("```") or line.startswith("'''")):
                # end of block
                line0 = block.split("\n")[0]
                block2 = "\n".join(block.split("\n")[1:])
                if line0.startswith("!!!"):
                    methodcode = line0[3:]
                    methodcode = methodcode.rstrip(", )")  # remove end )
                    methodcode = methodcode.replace("(", "(self,")
                    if not methodcode.strip() == line0[3:].strip():
                        # means there are parameters
                        methodcode += ",content=block2)"
                    else:
                        methodcode += "(content=block2)"
                    methodcode = methodcode.replace(",,", ",")

                    # print("methodcode:'%s'" % methodcode)
                    if line0[3:].strip().strip(".").strip(",") == "":
                        self._processData(block2)
                        block = ""
                    else:
                        cmd = "j.tools.docgenerator.macros." + methodcode
                        print(cmd)
                        try:
                            block = eval(cmd)
                        except Exception as e:
                            from IPython import embed
                            print("DEBUG NOW eval macro in doc")
                            embed()
                            raise RuntimeError("stop debug here")
                            raise e
                else:
                    codeblocks.append(block)
                    block = "***[%s]***\n" % (len(codeblocks) - 1)

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

        out = out.replace("{{%", "[[%")
        out = out.replace("}}%", "]]%")
        out = pystache.render(out, self.data)
        out = out.replace("[[%", "{{%")
        out = out.replace("]]%", "}}%")

        for x in range(len(codeblocks)):
            out = out.replace("***[%s]***\n" % x, "```\n%s\n```\n" % codeblocks[x])

        self.content = out

    def process(self):
        self.processDefaultData()

        if self.defaultContent != "":
            content = self.defaultContent
            if content[-1] != "\n":
                content += "\n"
        else:
            content = ""
        self.content = content
        self.content += j.sal.fs.fileGetContents(self.path)

        for i in range(3):
            self.processContent()  # dirty hack to do iterative behaviour for processing macro's. but is ok

    def write(self, docSite):

        if self.show:

            C = "+++\n"
            C += toml.dumps(self.data)
            C += "\n+++\n\n"

            # C+=

            C += self.content

            dpath = j.sal.fs.joinPaths(docSite.outpath, "content", self.rpath)
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
