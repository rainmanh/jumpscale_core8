from JumpScale import j
import textwrap

app = j.tools.cuisine._getBaseAppClass()


class CuisineJumpscale(app):
    NAME = None
    VERSION = None

    _env_template = '''\
    if [ -n "$JSBASE" ]; then
        return 0
    fi
    _ORIG_PATH="$PATH"
    _ORIG_PYTHONPATH="$PYTHONPATH"
    _ORIG_PYTHONHOME="$PYTHONHOME"
    _ORIG_LD_LIBRARY_PATH="$LD_LIBRARY_PATH"
    _ORIG_PS1="$PS1"

    _reset() {{
        name=$1
        orig_name="_ORIG_$name"
        if [ -n "${{!orig_name}}" ]; then
            export $name="${{!orig_name}}"
        else
            unset $name
        fi
        unset $orig_name
    }}

    deactivate() {{
        unset JSBASE
        _reset "PATH"
        _reset "PYTHONPATH"
        _reset "PS1"
        _reset "PYTHONHOME"
        _reset "LD_LIBRARY_PATH"
        if [ -n "$BASH" -o -n "$ZSH_VERSION" ] ; then
            hash -r 2>/dev/null
        fi
        unset -f deactivate
    }}

    export PATH={root}/bin:$PATH
    export JSBASE={root}
    export PYTHONPATH={root}/lib:{root}/lib/lib-dynload/:{root}/bin:{root}/lib/python.zip:{root}/lib/plat-x86_64-linux-gnu
    export PYTHONHOME={root}/lib
    export LD_LIBRARY_PATH={root}/bin
    export PS1="(JumpScale7)$PS1"

    # This should detect bash and zsh, which have a hash command that must
    # be called to get it to forget past commands.  Without forgetting
    # past commands the $PATH changes we made may not be respected
    if [ -n "$BASH" -o -n "$ZSH_VERSION" ] ; then
            hash -r 2>/dev/null
    fi
    '''

    _jspython_template = '''\
    #!/bin/bash
    # set -x
    source {root}/env.sh
    exec $JSBASE/bin/python2.7 "$@"
    '''

    _system_hrd_template = '''\
    paths.base={root}
    paths.bin=$(paths.base)/bin
    paths.code={code}
    paths.lib=$(paths.base)/lib

    paths.python.lib.js=$(paths.lib)/JumpScale
    paths.python.lib.ext=$(paths.base)/libext
    paths.app=$(paths.base)/apps
    paths.var=$(paths.base)/var
    paths.log=$(paths.var)/log
    paths.pid=$(paths.var)/pid

    paths.cfg=$(paths.base)/cfg
    paths.hrd=$(paths.base)/hrd

    system.logging = 1
    system.sandbox = 1
    '''

    _ays_hrd_template = '''\
    #here domain=jumpscale, change name for more domains
    metadata.jumpscale =
        url:'{url}',
        branch:'{branch}',
    '''

    _whoami_hrd_template = '''\
    email                   =
    fullname                =
    git.login               = 'ssh'
    git.passwd              = 'ssh'
    '''

    def _build_bin(self, root, repo='base_python'):
        url = 'http://git.aydo.com/binary/%s' % repo
        source = self.cuisine.development.git.pullRepo(url, depth=1)

        for name in ('lib', 'bin', 'env.sh'):
            self.cuisine.core.file_copy(
                j.sal.fs.joinPaths(source, 'root', name),
                root,
                recursive=True,
            )

    def _ensure_root(self, root):
        for directory in ['bin', 'lib', 'apps', 'hrd/system', 'hrd/apps']:
            self.cuisine.core.dir_ensure(
                j.sal.fs.joinPaths(root, directory)
            )

    def _build_js(self, source, root, branch):
        # copy jumpscale
        self.cuisine.core.file_copy(
            j.sal.fs.joinPaths(source, 'lib', 'JumpScale'),
            j.sal.fs.joinPaths(root, 'lib'),
            recursive=True,
        )

        # copy apps
        for file in ['apps/agentcontroller', 'apps/jsagent', 'apps/osis']:
            self.cuisine.core.file_copy(
                j.sal.fs.joinPaths(source, file),
                j.sal.fs.joinPaths(root, 'apps'),
                recursive=True,
            )

        # copy install tools
        for file in ['install/InstallTools.py', 'install/ExtraTools.py']:
            self.cuisine.core.file_copy(
                j.sal.fs.joinPaths(source, file),
                j.sal.fs.joinPaths(root, 'lib', 'JumpScale'),
                recursive=True,
            )

        # write jspython
        self.cuisine.core.file_write(
            j.sal.fs.joinPaths(root, 'bin', 'jspython'),
            textwrap.dedent(self._jspython_template.format(root=root)),
            mode=744,
        )

        # write env.sh
        self.cuisine.core.file_write(
            j.sal.fs.joinPaths(root, 'env.sh'),
            textwrap.dedent(self._env_template.format(root=root)),
            mode=744,
        )

    def _build_cfg(self, source, root):
        self.cuisine.core.file_write(
            j.sal.fs.joinPaths(root, 'hrd', 'system', 'system.hrd'),
            textwrap.dedent(self._system_hrd_template.format(
                root=root,
                code='/opt/code',
            ))
        )

        self.cuisine.core.file_write(
            j.sal.fs.joinPaths(root, 'hrd', 'system', 'atyourservice.hrd'),
            textwrap.dedent(
                self._ays_hrd_template.format(
                    url='https://github.com/jumpscale7/ays_jumpscale7.git',
                    branch='master',
                )
            )
        )

        self.cuisine.core.file_write(
            j.sal.fs.joinPaths(root, 'hrd', 'system', 'whoami.hrd'),
            textwrap.dedent(
                self._whoami_hrd_template
            )
        )

    def _build_shellcmds(self, source, root):
        # copy shellcmds
        root = root.replace('/', r'\/')
        for file in self.cuisine.core.fs_find(j.sal.fs.joinPaths(source, 'shellcmds'), type='f'):
            name = j.sal.fs.getBaseName(file)
            self.cuisine.core.run(
                r'sed "s/\/usr\/bin\/env jspython/{root}\/bin\/jspython/" {file} > {root}/bin/{name} && chmod a+x {root}/bin/{name}'.format(
                    root=root, file=file, name=name
                )
            )

    def build(self, root='/opt/jumpscale7', branch='master'):
        self.cuisine.core.dir_ensure(root)
        self._ensure_root(root)

        self._build_bin(root)

        # TODO: Fix debug section
        # clone jumpscale
        # url = 'https://github.com/jumpscale7/jumpscale_core7'
        #
        # source = self.cuisine.development.git.pullRepo(
        #     url, depth=1, branch=branch
        # )
        source = '/opt/code/github/jumpscale7/jumpscale_core7/'

        self._build_js(source, root, branch)
        self._build_cfg(source, root)
        self._build_shellcmds(source, root)
