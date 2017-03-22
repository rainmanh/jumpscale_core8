from JumpScale import j

import pystache


class Doc:
    """
    """

    def __init__(self, path, name, docSite):
        self.path = path
        self.name = name
        self.docSite = docSite

    def process(self):
        content = j.sal.fs.fileGetContents(self, path)
        self.last_content = content
        self.last_path = path
        self.last_dest = j.sal.fs.joinPaths(j.sal.fs.getDirName(path), j.sal.fs.getBaseName(path)[1:])
        # self.last_dest=j.sal.fs.joinPaths(self.root,j.sal.fs.pathRemoveDirPart(path,self.source))
        # j.sal.fs.createDir(j.sal.fs.getDirName(self.last_dest))

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
                result = eval("self.macros." + methodcode)
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
                    methodcode += ",content=block)"
                    methodcode = methodcode.replace(",,", ",")
                    try:
                        block = eval("self.macros." + methodcode)
                    except Exception as e:
                        raise e
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

        content = pystache.render(content, self.data)

        j.sal.fs.writeFile(filename=self.last_dest, contents=content)

        # j.data.regex.replace(regexFind, regexFindsubsetToReplace, replaceWith, text)

    def __repr__(self):
        return "doc:%s:%s" % (self.name, self.path)

    __str__ = __repr__
