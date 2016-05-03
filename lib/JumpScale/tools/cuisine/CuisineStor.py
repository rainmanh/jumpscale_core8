from JumpScale import j



class CuisineStor():

    def __init__(self, executor, cuisine):
        self.executor = executor
        self.cuisine = cuisine
        self.root="/storage/jstor/"

        self._config=None

        self.storagespaces={}  #paths of root of hash tree

    @property
    def config(self):
        if self._config==None:
            #read j.sal.fs.joinPaths(self.root,"config.yaml")
            #is dict, deserialize and store in self._config
            pass
        
        return self._config

    @config.setter
    def config(self, val):
        #check dict
        #store in config also remote serialized !!!
        pass

    def enableServerHTTP(self):
        self.config["httpserver"] = {"running": False}

    def enableServerREST(self):
        self.config["restserver"]={"running":False}

    def enableServerRSYNC(self):
        self.config["rsyncserver"] = {"running": False}

    def getStorageSpace(self,name):
        if not name in self.storagespaces:
            sp = StorSpace(self, name)
            self.storagespaces[name] = sp
        
        return self.storagespaces[name]


    def get(self, name, key, dest):
        """
        """
        sp = self.getStorageSpace(name)
        return sp.get(key, dest)

    def set(self, name, source, expiration=0, tags=""):
        """
        """
        sp = self.getStorageSpace(name)
        return sp.set(source, expiration, tags)

    def delete(self, name, key):
        pass


    def check(self, name, key):
        pass

    def restart(self):
        self.stop()
        self.start()


    def start(self):
        for key, stor in self.storagespaces.items():
            #... create rsync & caddy config file & send to remote server
            pass
        
        if "httpserver" in self.config:
            if self.config["httpserver"]["running"] == False:
                #start caddy in tmux, there should be cuisine extension for this
                pass
                
        if "rsyncserver" in self.config:
            if self.config["rsyncserver"]["running"] == False:
                #start rsync in tmux, there should be cuisine extension for this
                pass

    def exists(self, name, keys=[]):
        """
        """
        #create bash or python script which checks existance all keys on remote (this to be efficient, only 1 script execute remotely returns result required)
        #return list of which keys exist
        pass

    def check(self, name, keys=[]):
        """
        """
        #create bash or python script which checks all keys on remote (this to be efficient, only 1 script execute remotely returns result required)
        #check means hash check & existance check & expiration check 
        #return list of which keys exist & are as such ok
        pass

    def upload(self, name, plistname, source="/", excludes=["\.pyc","__pycache__"], removetmpdir=True, metadataStorspace=None):
        """
        - rsync over ssh the source to $tmpdir/cuisinestor/$plistname.   (from remote machine to local one)
        - create a plist like we do for aydostor or G8stor
        - do a self.exists ... to find which files are not on remote yet
        - create tar with all files which do not exist
            - aa/bb/...
            - compress each individual file using same compression as what we used for aydostor/g7stor (was something good)
        - upload tar to remote temp space
        - expand tar to required storage space
        - upload plist to storspace under plist/$plistname.plist (using file_upload)
            - metadataStorspace!=None then use other storspace for uploading the plist
        - remove tmpdir if removetmpdir=True
        """
        #@todo (*1*) implement
        pass

    def download(self, name, plistname, destination="/mnt/", removetmpdir=True, cacheStorspace=None):
        """
        - download plist on remote stor (use storspace.filedownload())
        - if cacheStorspace not None: check which files we already have in the cache (use cacheStorspace.exists)
        - create a bash or python file which has commands to get required files & put in tar on remote
        - download tar
        - if cacheStorspace!=None: upload each file to restore not in cache yet to cache
        - restore the files to $tmpdir/cuisinestor/$plistname  (all files, from cache & from remote, as efficient as possible)
            - decompress each file
        - rsync over ssh $tmpdir/cuisinestor/$plistname  to the cuisine we are working on
        - remove tmpdir if removetmpdir=True
        """
        #@todo (*1*) implement
        pass



def StorSpace():
    """
    each file is stored in

    $self.path/ab/cd/$hash
    ab & cd are first 2 and then next 2 hash chars

    OPTIONALLY:
    $self.path/ab/cd/$hash.meta is stored which has some metadata about the file


    """

    def __init__(self,stor,name):
        self.stor = stor
        self.path = j.sal.fs.joinPaths(stor.root, name)
        self._config = None
        self.init()
        self.config["PUBLIC"] = public
        # self.config[""]

    def init(self):
        """
        create
            /aa/aa/...
            /aa/ab/...
        structure
        """
        if "STATE" not in self.config:
            self.config["STATE"] = {"INITOK": False, "HTTP": False}

        if not self.config["STATE"]["INITOK"]:
            #...createDir(self.path)
            #@todo ...
            self.config["STATE"]["INITOK"] = True

        self.start()

    def enableServerHTTP(self,name,browse=True,secrets=[]):
        if "HTTP" not in self.config:
            self.config["HTTP"] = {}
        
        self.config["HTTP"][name] = {"secrets": secrets, "browse": browse}
        #make sure we only configure caddy when this entry exists
        #when browse false then users can download only when they know the full path
        #secrets is http authentication

        #there can be multiple entries for webserver un different names e.g. 1 browse with passwd, 1 anonymous with no browse, ...

    def enableServerRSYNC(self, name, browse=True, secrets=[]):
        if "RSYNC" not in self.config:
            self.config["RSYNC"] = {}
        
        self.config["RSYNC"][name] = {"secrets": secrets, "browse": browse}


    @property
    def config(self):
        if self._config == None:
            #read j.sal.fs.joinPaths(self.path,"config.yaml")
            #is dict, deserialize and store in self._config
            pass
        
        return self._config

    @config.setter
    def config(self, val):
        #check dict
        #store in config also remote serialized !!!
        pass

    def file_upload(self, source, storpath, expiration=0, tags=""):
        #upload file to $self.path/$storpath  storpath is relative e.g. myfiles/something/read.this
        pass

    def file_download(self, storpath, dest, expiration=0, tags=""):
        #download file from $self.path/$storpath  to dest which is local
        pass

    def file_remove(self, storpath):
        pass

    def upload(self, source, dest, expiration=0, tags=""):
        #upload file to $self.path/$dest  dest is relative e.g. myfiles/something/read.this
        pass

    def exists(self, keys=[]):
        #description see stor above
        pass

    def checks(self):
        #description see stor above, BE EFFICIENT
        pass

    def get(self, key, dest, chmod="", chown=""):
        """
        """
        #find/download the right file & put on destination
        pass

    def set(self, source, expiration=0, tags=""):
        """
        """
        #upload file to right location
        if expiration!=0 or tags!="":
            meta = {}
            meta["expiration"] = expiration
            meta["tags"] = tags
            #serialize to yaml store as $self.path/ab/cd/$hash.meta

    def delete(self, key):
        pass


    def check(self, key):
        #check expiration, if old remove
        #remotely check hash, check if ok with filename
        pass


    def getMetadata(self, keys):
        """
        """
        #create bash or python script which gets metadata for all files specified and puts in tgz
        #dowbload tgz
        #expand and put in list of dicts, return the list
        #this is done to be more efficient
        #only return when metadata exists
        pass


    def setMetadata(self, keys, metadata={}):
        """
        @param metadata is the dict which is relevant for the files mentioned
        """
        #create bash or python script which sets metadata for all files specified
        pass


"""
some remarks

- all upload/download use the cuisine base classes (not the optionally enabled rsync or httpserver on the stor)

"""
