from JumpScale import j
import gzip

class StorScripts():
    # create hexa directory tree
    # /00/00, /00/01, /00/02, ..., /ff/fe, /ff/ff
    def initTree(self, root):
        return """
        import os
        
        root = "%s"
        for a in range(0, 256):
            lvl1 = os.path.join(root, format(a, '02x'))
            os.mkdir(lvl1)
            
            for b in range(0, 256):
                lvl2 = os.path.join(lvl1, format(b, '02x'))
                os.mkdir(lvl2)
        
        """ % root
    
    # check if a set of keys exists
    def exists(self, root, keys):
        return """
        import os
        import json
        
        root = "%s"
        keys = json.loads('''%s''')
        data = {}
        
        def hashPath(root, hash):
            return os.path.join(root, hash[:2], hash[2:4], hash)
        
        for key in keys:
            data[key] = os.path.isfile(hashPath(root, key))
        
        print(json.dumps(data))
        
        """ % (root, j.data.serializer.json.dumps(keys))
    
    def check(self, root, keys):
        return """
        import os
        import json
        import hashlib
        import time
        
        root = "%s"
        keys = json.loads('''%s''')
        data = {}
        
        def hashfile(filename, blocksize=65536):
            afile = open(filename, 'rb')
            hasher = hashlib.md5()
            buf = afile.read(blocksize)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(blocksize)
            
            afile.close()
            return hasher.hexdigest()
        
        def loadMetadata(metafile):
            with open(metafile, 'r') as f:
                data = f.read()
            
            return json.loads(data)
                
        def checkMeta(fullpath):
            metafile = fullpath + ".meta"
            metadata = loadMetadata(metafile)
            
            if time.time() >= metadata["expiration"]:
                # os.unlink(fullpath)
                # os.unlink(metafile)
                return "expired"
            
            return True
        
        def checkFile(dirname, filename):
            fullpath = os.path.join(dirname, filename)
            
            if not os.path.isfile(fullpath):
                return "not found"
            
            if hashfile(fullpath) != os.path.basename(filename):
                # os.unlink(fullpath)
                # delete metafile if exists ?
                return "corrupted"
            
            if os.path.isfile(fullpath + ".meta"):
                return checkMeta(fullpath)
            
            return True
        
        def checkContent(root):
            for dirname, dirnames, filenames in os.walk(root):
                for filename in filenames:
                    if filename.endswith(".meta"):
                        continue
                    
                    data[filename] = checkFile(dirname, filename)
        
        # check the whole storagespace
        if len(keys) == 0:
            for a in range(0, 256):
                lvl1 = os.path.join(root, format(a, '02x'))
                
                for b in range(0, 256):
                    checkContent(os.path.join(lvl1, format(b, '02x')))
        
        # check for specific keys
        else:
            for key in keys:
                path = os.path.join(key[:2], key[2:4], key)
                data[key] = checkFile(root, path)
        
        print(json.dumps(data))
        
        """ % (root, j.data.serializer.json.dumps(keys))
    
    def getMetadata(self, root, keys):
        return """
        import os
        import json
        import gzip
        import random
        
        root = "%s"
        keys = json.loads('''%s''')
        data = {}
        
        def loadMetadata(metafile):
            with open(metafile, 'r') as f:
                data = f.read()
            
            return json.loads(data)
        
        def getMetadata(dirname, filename, key):
            fullpath = os.path.join(dirname, filename)
            metapath = fullpath + ".meta"
            
            if os.path.isfile(metapath):
                data[key] = loadMetadata(metapath)
        
        for key in keys:
            path = os.path.join(key[:2], key[2:4], key)
            getMetadata(root, path, key)
        
        output = json.dumps(data)
        content = gzip.compress(bytes(output, 'utf-8'))
        tmpfile = '/tmp/md-gzip-' + str(random.randrange(1, 10000000)) + '.gz'
        
        with open(tmpfile, 'w+b') as f:
            f.write(content)
        
        print(tmpfile)
            
        """ % (root, j.data.serializer.json.dumps(keys))
        
class CuisineStor():
    def __init__(self, executor, cuisine):
        self.executor = executor
        self.cuisine = cuisine
        self.root = "/storage/jstor/"

        self._config = None
        self.scripts = StorScripts()

        self.storagespaces = {}  # paths of root of hash tree

    @property
    def config(self):
        if self._config == None:
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

    def enableServerRSYNC(self):
        self.config["rsyncserver"] = {"running": False}

    def existsStorageSpace(self, name):
        """
        Check if specific storagespace exists
        """
        return self.cuisine.core.dir_exists(j.sal.fs.joinPaths(self.root, name))

    def getStorageSpace(self, name):
        """
        Return a storagespace object
        """
        if not name in self.storagespaces:
            sp = StorSpace(self, name)
            self.storagespaces[name] = sp
        
        return self.storagespaces[name]


    def get(self, name, key, dest):
        """
        Download a file from a specific storagespace
        """
        sp = self.getStorageSpace(name)
        return sp.get(key, dest)

    def set(self, name, source, expiration=0, tags=""):
        """
        Upload a file in a specific storagespace
        """
        sp = self.getStorageSpace(name)
        return sp.set(source, expiration, tags)

    def delete(self, name, key):
        """
        Delete a file in a specific storagespace
        """
        sp = self.getStorageSpace(name)
        return sp.delete(key)
    
    def removeStorageSpace(self, name):
        """
        Remove a complete storagespace and all it's content
        """
        if not self.existsStorageSpace(name):
            return None
        
        path = j.sal.fs.joinPaths(self.root, name)
        self.cuisine.core.dir_remove(path, recursive=True)
        
        if name in self.storagespaces:
            del self.storagespaces[name]

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
        Check if a keys exists in a specific storagespace
        """
        sp = self.getStorageSpace(name)
        return sp.exists(keys)

    def check(self, name, keys=[]):
        """
        Check a set of keys (or all keys if not specified).
        Check consist of an existance, consistancy (checksum) check and expiration rotation
        Return a list of keys found and still valid
        """
        #create bash or python script which checks all keys on remote (this to be efficient, only 1 script execute remotely returns result required)
        #check means hash check & existance check & expiration check 
        #return list of which keys exist & are as such ok
        sp = self.getStorageSpace(name)
        return sp.check(keys)

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

class StorSpace(object):
    """
    each file is stored in

    $self.path/ab/cd/$hash
    ab & cd are first 2 and then next 2 hash chars

    OPTIONALLY:
    $self.path/ab/cd/$hash.meta is stored which has some metadata about the file


    """

    def __init__(self, stor, name, public=True):
        self.cuisine = stor.cuisine
        self.executor = stor.executor
        self.stor = stor
        
        self.path = j.sal.fs.joinPaths(stor.root, name)
        self._config = {}
        
        self.init()
        # self.config["public"] = public
        # self.config[""]

    def init(self):
        if "setup" not in self.config:
            self.config["setup"] = {"initialized": False, "http": False}

        if not self.config["setup"]["initialized"]:
            self.cuisine.core.dir_ensure(self.path)
            
            # create a full empty directory tree
            script = self.stor.scripts.initTree(self.path)
            self.cuisine.core.execute_python(script)
            self.config["setup"]["initialized"] = True
        
        self.configCommit()
        
        # self.start()

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
        if self._config == {}:
            path = j.sal.fs.joinPaths(self.path, "config.yaml")
            
            if self.cuisine.core.file_exists(path):
                yaml = self.cuisine.core.file_read(path)
                self._config = j.data.serializer.yaml.loads(yaml)
        
        return self._config

    """
    @config.setter
    def config(self, val):
        import ipdb; ipdb.set_trace()
        #check dict
        #store in config also remote serialized !!!
        pass
    """
    def configCommit(self):
        yaml = j.data.serializer.yaml.dumps(self.config)
        path = j.sal.fs.joinPaths(self.path, "config.yaml")
        self.cuisine.core.file_write(path, yaml)
    
    def hashPath(self, hash):
        return '%s/%s/%s' % (hash[:2], hash[2:4], hash)
        
    def metadataFile(self, path):
        return "%s.meta" % path
    
    def metadata(self, expiration=None, tags=None):
        """
        Build a representation used internaly to expose metadata
        """
        if expiration or tags:
            meta = {}
            meta["expiration"] = expiration
            meta["tags"] = tags
            return meta
            
        return None
        
    def file_upload(self, source, storpath, expiration=None, tags=None):
        """
        Upload a file to a specific location in the storagespace
        @param expiration: timestamp after when file could be discarded
        """
        # small protection against directory transversal
        # better approch: os.path.abspath ?
        storpath = storpath.replace('../', '')
        
        filepath = j.sal.fs.joinPaths(self.path, storpath)
        path = j.sal.fs.getDirName(filepath)
        
        # be sur that remote directory exists
        self.cuisine.core.dir_ensure(path)
        self.cuisine.core.file_upload_binary(source, filepath)
        
        metadata = self.metadata(expiration, tags)
        if metadata:
            # upload metadata only if defined
            # NOTE: metadata are saved in json because code executed
            # on remote side does probably not have yaml parser installed
            # json parser in python should be able out-of-box
            md = j.data.serializer.json.dumps(metadata)
            self.cuisine.core.file_write(self.metadataFile(filepath), md)
        
        return True

    def file_download(self, storpath, dest, chmod=None, chown=None):
        """
        Download a file from the storagespace to a specific location
        """
        # small protection against directory transversal
        storpath = storpath.replace('../', '')
        
        filepath = j.sal.fs.joinPaths(self.path, storpath)
        self.cuisine.core.file_download_binary(dest, filepath)
        
        if chmod:
            j.sal.fs.chmod(dest, chmod)

        if chown:
            # FIXME: group ?
            j.sal.fs.chown(dest, chown)
        
        # checking if there is metadata
        metafile = self.metadataFile(storpath)
        if self.cuisine.core.file_exists(metafile):
            return self.cuisine.core.file_read(metafile)
        
        return True

    def file_remove(self, storpath):
        """
        Remove a given file from the storagespace
        """
        # small protection against directory transversal
        storpath = storpath.replace('../', '')
        
        path = j.sal.fs.joinPaths(self.path, storpath)
        
        if not self.cuisine.core.file_exists(path):
            return False
        
        # remove file
        self.cuisine.core.file_unlink(path)
        
        # remove metadata if exists
        metadata = self.metadataFile(path)
        if self.cuisine.core.file_exists(metadata):
            self.cuisine.core.file_unlink(metadata)
        
        return True

    def exists(self, keys=[]):
        """
        Check if a set of keys exists. Returns a list which contains hash and bool
        """
        script = self.stor.scripts.exists(self.path, keys)
        data = self.cuisine.core.execute_python(script)
        return j.data.serializer.json.loads(data)

    def get(self, key, dest, chmod=None, chown=None):
        """
        Download a specific key (hash) from storage and save it locally
        """
        return self.file_download(self.hashPath(key), dest, chmod, chown)

    def set(self, source, expiration=None, tags=None):
        """
        Upload a file and save it to the storage. It's hash will be returned
        @param expiration: timestamp after when file could be discarded
        """
        checksum = j.data.hash.md5(source)
        
        # do not upload file if already exists
        existing = self.exists([checksum])
        if existing[checksum]:
            return True
        
        hashpath = self.hashPath(checksum)
        
        # uploading file, if success, return the hash
        if self.file_upload(source, hashpath, expiration, tags):
            return checksum
        
        return False

    def delete(self, key):
        """
        Delete a key in the storagespace
        """
        return self.file_remove(self.hashPath(key))

    def check(self, keys=[]):
        """
        Check consistancy and validity of a set of keys in the storagespace
        """
        script = self.stor.scripts.check(self.path, keys)
        data = self.cuisine.core.execute_python(script)
        return j.data.serializer.json.loads(data)

    def getMetadata(self, keys):
        """
        Get metadata content for a set of keys from the storagespace
        """
        script = self.stor.scripts.getMetadata(self.path, keys)
        data = self.cuisine.core.execute_python(script)
        print(data)
        
        if not data.startswith('/tmp'):
            # output seems not correct
            return False
        
        localfile = '/tmp/jstor-md.gz'
        self.cuisine.core.file_download_binary(localfile, data)
        self.cuisine.core.file_unlink(data)
        
        with open(localfile, 'rb') as f:
            content = f.read()
        
        j.sal.fs.remove(localfile)
        
        metadata = gzip.decompress(content).decode('utf-8')
        
        return j.data.serializer.json.loads(metadata)


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
