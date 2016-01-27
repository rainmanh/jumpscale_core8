from JumpScale import j
import requests
from urllib.parse import urljoin, urlparse


class StorxFactory(object):
    def __init__(self,):
        super(StorxFactory, self).__init__()
        self.__jslocation__ = "j.clients.storx"

    def get(self, base_url):
        return StorxClient(base_url)


class StorxClient(object):
    """Client for the AYDO Stor X"""
    def __init__(self, base_url):
        super(StorxClient, self).__init__()
        o = urlparse(base_url)
        self.base_url = o.geturl()
        self.path = o.path

    def _getURL(self, path):
        return urljoin(self.base_url, j.sal.fs.joinPaths(self.path, path))

    def putFile(self, namespace, file_path):
        """
        Upload a file to the store

        @namespace: str, namespace
        @file_path: str, path of the file to upload
        return: str, md5 hash of the file
        """
        url = self._getURL(namespace)
        resp = None
        with open(file_path, 'rb') as f:
            # streaming upload, avoid reading all file in memory
            resp = requests.post(url, data=f, headers={'Content-Type': 'application/octet-stream'})
            resp.raise_for_status()

        return resp.json()["Hash"]

    def getFile(self, namespace, hash, destination):
        """
        Retreive a file from the store and save it to a file

        @namespace: str, namespace
        @hash: str, hash of the file to retreive
        """
        url = urljoin(self.base_url, "%s/%s" % (namespace, hash))
        resp = requests.get(url, stream=True)

        resp.raise_for_status()

        with open(destination, 'wb') as fd:
            for chunk in resp.iter_content(65536):
                fd.write(chunk)

        return True

    def deleteFile(self, namespace, hash):
        """
        Delete a file from the Store

        @namespace: str, namespace
        @hash: str, hash of the file to delete
        """
        url = urljoin(self.base_url, "%s/%s" % (namespace, hash))
        resp = requests.delete(url)

        resp.raise_for_status()

        return True

    def existsFile(self, namespace, hash):
        """
        Test if a file exists
        @namespace: str, namespace
        @hash: str, hash of the file to test
        return: bool
        """
        url = urljoin(self.base_url, "%s/%s" % (namespace, hash))
        resp = requests.head(url)

        if resp.status_code == requests.codes.ok:
            return True
        elif resp.status_code == requests.codes.not_found:
            return False
        else:
            resp.raise_for_status()

    def existsFiles(self, namespace, hashes):
        """
        Test if a list of file exists

        @namespace: str, namespace
        @hashes: list, list of hashes to test
        return: dict, directory with keys as hashes and value boolean indicating of hash exists or not
        example :
            {'7f820c17fa6f8beae0828ebe87ef238a': True,
            'a84da677c7999e6bed29a8b2d9ebf0e3': True}

        """
        url = urljoin(self.base_url, "%s/%s" % (namespace, "exists"))
        data = {'Hashes': hashes}
        resp = requests.post(url, json=data)

        resp.raise_for_status()

        return resp.json()

    def listNameSpace(self, namespace, compress=False, quality=6):
        """
        Retreive list of all file from a namespace

        @namespace: str, namespace
        @compress: bool, enable compression of the files
        @quality: int, if compress is enable, defined the quality of compression.
            low number is fast but less efficent, hight number is slow but best compression
        """
        url_params = {
            'compress': compress,
            'quality': quality,
        }
        url = urljoin(self.base_url, namespace)
        resp = requests.get(url, params=url_params)

        resp.raise_for_status()

        return resp.json()
