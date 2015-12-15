#BOOTSTRAP CODE


import os
import time

if "JSBRANCH" in os.environ:
    branch=os.environ["JSBRANCH"]
else:
    branch="master"

if "TMPDIR" in os.environ:
    tmpdir=os.environ["TMPDIR"]
else:
    tmpdir="/tmp"

os.chdir(tmpdir)

print("bootstrap installtools in dir %s and use branch:'%s'"%(tmpdir,branch))

#GET THE MAIN INSTALL TOOLS SCRIPT

path="%s/InstallTools.py"%tmpdir

overwrite=True #set on False for development or debugging

if overwrite and os.path.exists(path):
    os.remove(path)
    # os.remove(path+"c")

import random

if not os.path.exists(path):
    print("overwrite")
    r=random.randint(1, 10000)#to make sure caching does not work on internet
    os.popen("curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/%s/install/InstallTools.py?%s > %s"%(branch,r,path))
    time.sleep(2)

InstallTools = __import__('InstallTools')
do = InstallTools.do

#look at methods in https://github.com/Jumpscale/jumpscale_core8/blob/master/install/InstallTools.py to see what can be used
#there are some easy methods to allow git manipulation, copy of files, execution of items

#there are many more functions available in jumpscale

#FROM now on there is a do. variable which has many features, please investigate


if "DEVELOP" in os.environ:
    do.installer.prepareUbuntu15Development()

print("install jumpscale8")
do.installer.installJS()

from JumpScale import j

#j.system....
