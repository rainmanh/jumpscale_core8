# from JumpScale import j
#
#
# base = j.tools.cuisine._getBaseClass()
#
#
# class CuisineBuilder(base):
#
#     def __init__(self, executor, cuisine):
#         self.executor = executor
#         self.cuisine = cuisine
#
#     # TODO: *3 seems to be some double functionality with cuisinsandbox class but lets leave for now
#
#     def all(self, start=False, sandbox=False, stor_addr=None, stor_name=""):
#         if self.cuisine.core.isMac and not stor_name:
#             stor_name = "osx10.11"
#         self.cuisine.development.python.install()
#         if not self.cuisine.systemservices.js8_g8os.jumpscale_installed():
#             self.cuisine.systemservices.js8_g8os.jumpscale8()
#         self.cuisine.apps.mongodb.build(start=start)
#         self.cuisine.apps.portal.install(start=start)
#         self.cuisine.apps.redis.install()
#         self.cuisine.apps.redis.start()
#         if not self.cuisine.core.isMac:
#             self.cuisine.systemservices.g8oscore.build(start=start)
#             self.cuisine.systemservices.g8osfs.build(start=False)
#         self.cuisine.apps.syncthing.build(start=start)
#         self.cuisine.apps.controller.build(start=start)
#         self.cuisine.systemservices.aydostor.build(start=start)
#         self.cuisine.apps.etcd.build(start=start)
#         self.cuisine.apps.caddy.install(start=start)
#         # self.cuisine.apps.skydns(start=start)
#         self.cuisine.apps.influxdb.install(start=start)
#         self.cuisine.solutions.cockpit.install(start=False)
#         if not self.cuisine.core.isDocker and not self.cuisine.core.isLxc and not self.cuisine.core.isMac:
#             self.cuisine.apps.weave.build(start=start)
#         if sandbox:
#             if not stor_addr:
#                 raise j.exceptions.RuntimeError("Store address should be specified if sandboxing enable.")
#             self.sandbox(stor_addr, stor_name)
#
#     def sandbox(self, stor_addr, stor_name, python=True):
#         """
#         stor_addr : addr to the store you want to populate. e.g.: https://stor.jumpscale.org/storx
#         python : do you want to sandbox python too ? if you have segfault after trying sandboxing python, re run with python=False
#         """
#         # jspython is generated during install,need to copy it back into /opt before sandboxing
#         self.cuisine.core.file_copy('/usr/local/bin/jspython', '/opt/jumpscale8/bin')
#
#         # clean lib dir to avoid segfault during sandboxing
#         self.cuisine.core.dir_remove('%s/*' % self.cuisine.core.dir_paths['LIBDIR'])
#         self.cuisine.core.dir_ensure('%s' % self.cuisine.core.dir_paths['LIBDIR'])
#         if self.cuisine.core.isMac:
#             self.cuisine.core.file_link('/usr/local/lib/python3.5/site-packages/JumpScale/',
#                                          '%s/JumpScale' % self.cuisine.core.dir_paths['LIBDIR'])
#         else:
#             self.cuisine.core.file_link('/usr/local/lib/python3.5/dist-packages/JumpScale',
#                                          '%s/JumpScale' % self.cuisine.core.dir_paths['LIBDIR'])
#         self.cuisine.core.file_link("%s/github/jumpscale/jumpscale_portal8/lib/portal" %
#                                      self.cuisine.core.dir_paths["CODEDIR"], "%s/portal" % self.cuisine.core.dir_paths['JSLIBDIR'])
#
#         # start sandboxing
#         cmd = "j.tools.cuisine.local.builder.dedupe(['/opt'], '%s' + 'js8_opt', '%s', sandbox_python=%s)" % (
#             stor_name, stor_addr, python)
#         self.cuisine.core.run('js "%s"' % cmd)
#         url_opt = '%s/static/%sjs8_opt.flist' % (stor_addr, stor_name)
#
#         return url_opt
#
#     def sandbox_python(self, python=True):
#         self.log("START SANDBOX")
#         if self.cuisine.executor.type != "local":
#             raise j.exceptions.RuntimeError("only supports cuisine in local mode")
#         if python:
#             paths = []
#             if self.cuisine.core.isMac:
#                 paths.append("/usr/local/Cellar/python3/3.5.2/Frameworks/Python.framework/Versions/3.5/lib/python3.5")
#                 paths.append("/usr/local/lib/python3.5/site-packages")
#             else:
#                 paths.append("/usr/lib/python3.5/")
#                 paths.append("/usr/local/lib/python3.5/dist-packages")
#                 paths.append("/usr/lib/python3/dist-packages")
#
#             excludeFileRegex = ["-tk/", "/lib2to3", "-34m-", ".egg-info"]
#             excludeDirRegex = ["/JumpScale", "\.dist-info", "config-x86_64-linux-gnu", "pygtk"]
#
#             dest = j.sal.fs.joinPaths(self.cuisine.core.dir_paths['base'], 'lib')
#
#             for path in paths:
#                 j.tools.sandboxer.copyTo(path, dest, excludeFileRegex=excludeFileRegex, excludeDirRegex=excludeDirRegex)
#
#             if not j.sal.fs.exists("%s/bin/python" % self.cuisine.core.dir_paths['base']):
#                 if self.cusine.core.isMac:
#                     j.sal.fs.copyFile("/usr/local/bin/python3.5", "%s/bin/python" %
#                                       self.cuisine.core.dir_paths['base'])
#                 else:
#                     j.sal.fs.copyFile("/usr/bin/python3.5", "%s/bin/python" % self.cuisine.core.dir_paths['base'])
#
#         j.tools.sandboxer.sandboxLibs("%s/lib" % self.cuisine.core.dir_paths['base'], recursive=True)
#         j.tools.sandboxer.sandboxLibs("%s/bin" % self.cuisine.core.dir_paths['base'], recursive=True)
#         self.log("SANDBOXING DONE, ALL OK IF TILL HERE, A Segfault can happen because we have overwritten ourselves.")
#
#     def dedupe(self, dedupe_path, namespace, store_addr, output_dir='/tmp/sandboxer', sandbox_python=True):
#         if self.cuisine.executor.type != "local":
#             raise j.exceptions.RuntimeError("only supports cuisine in local mode")
#
#         self.cuisine.core.dir_remove(output_dir)
#
#         if sandbox_python:
#             self.sandbox_python()
#
#         if not j.data.types.list.check(dedupe_path):
#             dedupe_path = [dedupe_path]
#
#         for path in dedupe_path:
#             self.log("DEDUPE:%s" % path)
#             j.tools.sandboxer.dedupe(path, storpath=output_dir, name=namespace,
#                                      reset=False, append=True, excludeDirs=['/opt/code'])
#
#         store_client = j.clients.storx.get(store_addr)
#         files_path = j.sal.fs.joinPaths(output_dir, 'files')
#         files = j.sal.fs.listFilesInDir(files_path, recursive=True)
#         error_files = []
#         for f in files:
#             src_hash = j.data.hash.md5(f)
#             self.log('uploading %s' % f)
#             uploaded_hash = store_client.putFile(namespace, f)
#             if src_hash != uploaded_hash:
#                 error_files.append(f)
#                 self.log("%s hash doesn't match\nsrc     :%32s\nuploaded:%32s" % (f, src_hash, uploaded_hash))
#
#         if len(error_files) == 0:
#             self.log("all uploaded ok")
#         else:
#             raise RuntimeError('some files didnt upload properly. %s' % ("\n".join(error_files)))
#
#         metadataPath = j.sal.fs.joinPaths(output_dir, "md", "%s.flist" % namespace)
#         self.log('uploading %s' % metadataPath)
#         store_client.putStaticFile(namespace + ".flist", metadataPath)
