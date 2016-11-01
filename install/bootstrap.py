# BOOTSTRAP CODE


import os
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--no-reset', dest='no_reset', action='store_true', default=False,
                    help='clean JS')

args = parser.parse_args()

reset = not args.no_reset

if "JSBRANCH" in os.environ:
    branch = os.environ["JSBRANCH"]
else:
    branch = "master"

if "TMPDIR" in os.environ:
    tmpdir = os.environ["TMPDIR"]
else:
    tmpdir = "/tmp"

os.chdir(tmpdir)

print("bootstrap installtools in dir %s and use branch:'%s'" % (tmpdir, branch))

# GET THE MAIN INSTALL TOOLS SCRIPT

path = "%s/InstallTools.py" % tmpdir

if not os.path.exists(path):
    raise RuntimeError("Cannot find:%s" % path)

from importlib import util
spec = util.spec_from_file_location("InstallTools", path)

InstallTools = spec.loader.load_module()

do = InstallTools.do

# look at methods in https://github.com/Jumpscale/jumpscale_core8/blob/master/install/InstallTools.py to see what can be used
# there are some easy methods to allow git manipulation, copy of files, execution of items

# there are many more functions available in jumpscale

# FROM now on there is a do. variable which has many features, please investigate


# ALREADY DONE IN INSTALLJS
# print("prepare system for jumpscale8")
# do.installer.prepare()

print("install jumpscale8")
do.installer.installJS(clean=reset)

from JumpScale import j

# j.sal....
