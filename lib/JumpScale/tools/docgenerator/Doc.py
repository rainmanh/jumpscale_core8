from JumpScale import j
import toml
import pystache
import copy


class Doc:
    """
    """

    def __init__(self, path, name, docSite):
        self.path = path
        self.name = name.lower()
        self.nameOriginal = name
        self.docSite = docSite
        self.rpath = j.sal.fs.pathRemoveDirPart(path, self.docSite.path).strip("/")
        self.content = None
        self._defContent = ""
        self.data = {}
        self.show = True
        self.errors = []
        self.processed = False

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

    def processContent(self, iteration):
        j.tools.docgenerator.logger.info("process:%s" % self)
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

        # process multi line blocks
        state = "start"
        block = ""
        out = ""
        codeblocks = []
        dataBlock = ""
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
                        # means there was metadata data block in doc
                        dataBlock = block2
                        self._processData(block2)
                        block = ""
                    else:
                        cmd = "j.tools.docgenerator.macros." + methodcode
                        # print(cmd)
                        # block = eval(cmd)
                        try:
                            block = eval(cmd)
                        except Exception as e:
                            block = "```python\nERROR IN MACRO*** TODO: *1 ***\ncmd:\n%s\nERROR:\n%s\n```\n" % (cmd, e)
                            self.docSite.raiseError(block, doc=self)
                else:
                    codeblocks.append(block)
                    block = "***[%s]***\n" % (len(codeblocks) - 1)

                out += block
                block = ""
                state = "start"
                continue

            if state == "blockcomment":
                if line.startswith("-->"):
                    # end of comment
                    state = "start"
                continue

            if state == "blockstart":
                block += "%s\n" % line
                continue

            if state == "start" and (line.startswith("```") or line.startswith("'''")):
                state = "blockstart"
                continue

            print(line)
            if state == "start" and (line.startswith("<!-")):
                state = "blockcomment"
                continue

            out += "%s\n" % line

        out = out.replace("{{%", "[[%")
        out = out.replace("}}%", "]]%")
        out = pystache.render(out, self.data)
        out = out.replace("[[%", "{{%")
        out = out.replace("]]%", "}}%")

        dblock = j.data.serializer.toml.loads(dataBlock)

        if iteration == 0:  # important should only do this in first iteration
            rewriteDataBlock = False
            if "title" not in dblock:
                rewriteDataBlock = True
                name = self.nameOriginal.replace("_", " ").replace("-", " ").strip()
                # makes first letters uppercase
                name = " ".join([item[0].upper() + item[1:] for item in name.split(" ")])
                dblock["title"] = name
            if "date" not in dblock:
                rewriteDataBlock = True
                dblock["date"] = j.data.time.epoch2HRDate(j.data.time.epoch).replace("/", "-")
            if "tags" not in dblock:
                parts = [item.lower() for item in j.sal.fs.getDirName(self.path).strip("/").split("/")[-4:]]
                tags = []
                if "defs" in parts or "def" in parts:
                    tags.append("def")
                if "howto" in parts or "howtos" in parts:
                    tags.append("howto")
                if "ideas" in parts or "idea" in parts:
                    tags.append("idea")
                if "question" in parts or "questions" in parts:
                    tags.append("question")
                if "spec" in parts or "specs" in parts:
                    tags.append("spec")
                if "overview" in parts:
                    tags.append("overview")
                if "api" in parts or "apis" in parts:
                    tags.append("api")
                dblock["tags"] = tags
                rewriteDataBlock = True

            if rewriteDataBlock:
                content0 = j.sal.fs.fileGetContents(self.path)
                content1 = "\n```\n"
                content1 += "!!!\n"
                content1 += j.data.serializer.toml.dumps(dblock)
                content1 += "```\n"
                self._processData(j.data.serializer.toml.dumps(dblock))
                j.sal.fs.writeFile(filename=self.path, contents=content0 + content1)
                out += content1

        for x in range(len(codeblocks)):
            out = out.replace("***[%s]***\n" % x, "```\n%s\n```\n" % codeblocks[x])

        self.content = out

    def process3(self):
        # check links
        content = self.content
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
                    msg = "**ERROR: COULD NOT FIND LINK: %s TODO: **" % shortname
                    self.docSite.raiseError(msg, doc=self)
                    content = content.replace(match.founditem, msg)
                else:
                    thisdoc = self.docSite.docs[shortname]
                    content = content.replace(match.founditem, "](%s)" % (thisdoc.url))

        regex = "src *= *\" */?static"
        for match in j.data.regex.yieldRegexMatches(regex, content, flags=0):
            content = content.replace(match.founditem, "src = \"/")

        self.processed = True

    @property
    def title(self):
        if "title" in self.data:
            return self.data["title"]
        else:
            self.raiseError("Could not find title in doc.")

    @property
    def contentClean(self):
        if self.processed == False:
            self.write()
        # remove the code blocks (comments are already gone)
        state = "start"
        out = ""
        for line in self.content.split("\n"):
            if state == "blockstart":
                if (line.startswith("```") or line.startswith("'''")):
                    # end of block
                    state = "start"
                continue

            if state == "start" and (line.startswith("```") or line.startswith("'''")):
                state = "blockstart"
                continue

            out += "%s\n" % line
        out = out.replace("\n\n\n", "\n\n").replace("\n\n\n", "\n\n").replace("\n\n\n", "\n\n")
        return out

    @property
    def contentCleanSummary(self):
        c = self.contentClean
        lines = c.split("\n")
        counter = 0
        out = ""
        while counter < 20 and counter < len(lines):
            line = lines[counter]
            counter += 1
            if line.strip() == "" and counter > 10:
                return out
            if len(line) > 0 and line.strip()[0] == "#" and counter > 4:
                return out
            out += "%s\n" % line

        return out

    def raiseError(self, msg):
        return self.docSite.raiseError(msg, doc=self)

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
            self.processContent(iteration=i)  # dirty hack to do iterative behaviour for processing macro's. but is ok

    def processDefs(self):

        def ssplit(name):
            for item in " {[]}(),;:./?\"'$%^&*=!":
                if item in name:
                    name = name.split(item)[0]
            return name

        regex = "\$\$.*"  # find all possible images
        for match in j.data.regex.yieldRegexMatches(regex, self.content, flags=0):
            # print("##:%s" % match)
            defname = match.founditem
            defname0 = ssplit(defname.replace("$", ""))
            defname = defname0.lower().replace("_", "").replace("-", "").replace(" ", "")
            if defname in self.docSite.defs:
                def_ = self.docSite.defs[defname]
                defnew = "[%s](%s:%s.md)" % (def_.nameOriginal, def_.docSite.name, def_.nameOriginal)
                self.content = self.content.replace("$$" + defname0, defnew)
            else:
                defnew = "**ERROR: COULD NOT FIND DEF: %s**" % defname
                self.content = self.content.replace("$$" + defname0, defnew)
                self.docSite.raiseError(defnew, doc=self)

        self.process3()

    def write(self):

        if self.show:
            if self.errors != []:
                if "tags" not in self.data:
                    self.data["tags"] = ["error"]
                else:
                    self.data["tags"].append("error")

            C = "+++\n"
            C += toml.dumps(self.data)
            C += "\n+++\n\n"

            # C+=

            C += self.content

            dpath = j.sal.fs.joinPaths(self.docSite.outpath, "content", self.rpath)
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
