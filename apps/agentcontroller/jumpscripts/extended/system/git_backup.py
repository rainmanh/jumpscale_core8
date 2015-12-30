from JumpScale import j

descr = """
backup to gitlab
"""

organization = "jumpscale"
author = "khamisr@codescalers.com"
license = "bsd"
version = "1.0"
category = "system.git.backup"
period = 60*60*2
enable = True
async = True
roles = ["admin"]
queue ='io'

def action():
    import JumpScale.baselib.git
    import JumpScale.baselib.motherhip1_extensions

    project = j.sal.fs.joinPaths('/opt', 'code', 'git_incubaid')
    project = j.sal.fs.listDirsInDir(project)[0]
    
    path =  j.sal.fs.joinPaths(project, 'backup')
    gitcl = j.clients.git.getClient(project)

    j.tools.exporter.exportAll(path)

    message = '%s at %s' % (j.sal.fs.getBaseName(project), j.data.time.getLocalTimeHRForFilesystem())
    gitcl.commit(message)
    gitcl.push()