
from JumpScale import j
from dateutil import parser
import os
import httplib2
import io

try:
    from apiclient import discovery
except:
    j.do.execute("pip3 install google-api-python-client")
from apiclient import discovery
# from apiclient.http import *
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from GDriveFile import *
import os

SCOPES = ['https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/drive.appdata',
          'https://www.googleapis.com/auth/drive.scripts',
          'https://www.googleapis.com/auth/drive.metadata']

APPLICATION_NAME = 'Google Drive Exporter'


class GDriveFactory:

    def __init__(self):
        self.__jslocation__ = "j.clients.gdrive"
        self.logger = j.logger.get('j.clients.gdrive')

        self.secretsFilePath = 'gdrive_client_secrets.json'
        if not j.sal.fs.exists(self.secretsFilePath, followlinks=True):
            self.secretsFilePath = os.path.expanduser('~') + '/.gdrive_client_secrets.json'

        self.credentials = self._getCredentials()
        http = self.credentials.authorize(httplib2.Http())
        self.drive = discovery.build('drive', 'v3', http=http)
        self.files = self.drive.files()
        j.sal.fs.createDir('/tmp/gdrive/')

    def _getCredentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        store = Storage(self.secretsFilePath)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.secretsFilePath, SCOPES)
            flow.user_agent = APPLICATION_NAME
            credentials = tools.run(flow, store)
            self.logger.info('Storing credentials to ' + self.secretsFilePath)
        return credentials

    def fileExport(self, file_id, path=""):
        """

        file_id can be full id or url e.g. https://docs.google.com/document/d/asdfasdfasdgfadsfgY_gKZmXv2UbJtWrB3IEsJjfsUmCSvUQ/edit

        will check that path ends with e.g. docx, if not then will add

        download file in native office or markdown format
        - docx
        - xlsx
        - pptx
        - .md (is text)

        only supported is list above, ignore others

        """
        gfile = self.getFile(file_id)
        gfile.export(path)

    def fileExportPDF(self, file_id, path=""):
        gfile = self.getFile(file_id)
        gfile.exportPDF(path)

    def getFile(self, file_id):
        r = GDriveFile(id=file_id)
        return r

    def processMarkedDocs(self):
        """
        walk over google drive look for docs with <...> in name
        if empty <> then will create unique id of 4 chars
        will download the file to $datadir/gdrive/$letter1/$letter2/$id.pdf as pdf
        """
        page_token = None
        while True:
            # q="mimeType='image/jpeg'"
            # q = "'0B0OKOpLF52GNSUttdGFvdlFmNUE' in parents"
            q = "name contains '<' AND name contains '>' "
            response = self.files.list(q=q,
                                       spaces='drive',
                                       fields='nextPageToken, files(id, name, description, modifiedTime,version)',
                                       pageToken=page_token).execute()

            from IPython import embed
            print("DEBUG NOW 87")
            embed()
            raise RuntimeError("stop debug here")

            for file in response.get('files', []):
                # Process file & put metadata in file
                self.logger.info('Found gdrive file: %s (%s)' % (file.get('name'), file.get('id')))

                md = GDriveFile(id=file.get('id'), json=file.get('description'))
                print(md.json)

                # CHECK THAT FILE HAS BEEN MODIFIED
                epoch = int(j.data.time.any2epoch(parser.parse(file.get('modifiedTime'))))

                if epoch > md.modTime + 60 * 4:
                    self.logger.info("file modified, will export: %s" % md)
                    self.logger.info("%s>%s" % (epoch, md.modTime))
                    ddir = "/optvar/data/gdrive/%s%s" % (md.sid[0], md.sid[1])
                    j.sal.fs.createDir(ddir)
                    md.export(path="%s/%s.%s" % (ddir, md.sid, md.extension))
                    md.exportPDF(path="%s/%s.pdf" % (ddir, md.sid))
                    md.downloadDate = j.data.time.epoch
                    md.modTime = int(epoch)
                    md.changed = True
                    md.save()

            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
