from JumpScale import j
import requests
from requests.auth import HTTPBasicAuth
import os


class GrafanaFactory:

    def __init__(self):
        self.__jslocation__ = "j.clients.grafana"

    def get(self, url="http://localhost:3000", username="admin", password="admin", verify_ssl=True):
        return GrafanaClient(url, username, password, verify_ssl=verify_ssl)

    def getByInstance(self, instance=None):
        if instance is None or instance == '':
            service = j.atyourservice.findServices(
                role="grafana_client", first=True)
        else:
            service = j.atyourservice.findServices(
                role="grafana_client", instance=instance, first=True)
        hrd = service.hrd

        url = hrd.get("param.url")
        username = hrd.get("param.username")
        password = hrd.get("param.password")
        return self.get(url, username, password)


class GrafanaClient:

    def __init__(self, url, username, password, verify_ssl=True):
        self._url = url
        self.setAuth(username, password)
        self._verify_ssl = verify_ssl

    def ping(self):
        url = os.path.join(self._url, 'api/org/')
        try:
            self._session.get(url).json()
            return True
        except:
            return False

    def setAuth(self, username, password):
        self._username = username
        self._password = password
        auth = HTTPBasicAuth(username, password)
        self._session = requests.session()
        self._session.auth = auth

    def updateDashboard(self, dashboard):
        if j.data.types.string.check(dashboard):
            dashboard = j.data.serializer.json.loads(dashboard)
        url = os.path.join(self._url, 'api/dashboards/db')
        data = {'dashboard': dashboard, 'overwrite': True}
        result = self._session.post(url, json=data, verify=self._verify_ssl)
        return result.json()

    def listDashBoards(self):
        url = os.path.join(self._url, 'api/search/')
        return self._session.get(url, verify=self._verify_ssl).json()

    def isAuthenticated(self):
        url = os.path.join(self._url, 'api/org/')
        return self._session.get(url).status_code != 401

    def delete(self, dashboard):
        url = os.path.join(self._url, 'api/dashboards', dashboard['uri'])
        return self._session.delete(url, verify=self._verify_ssl)

    def changePassword(self, newpassword):
        url = os.path.join(self._url, 'api/user/password')
        data = {'newPassword': newpassword, 'oldPassword': self._password}
        result = self._session.put(url, json=data).json()
        self.setAuth(self._username, newpassword)
        return result

    def listDataSources(self):
        url = os.path.join(self._url, 'api/datasources/')
        return self._session.get(url, verify=self._verify_ssl).json()

    def addDataSource(self, data):
        url = os.path.join(self._url, 'api/datasources/')
        return self._session.post(url, json=data, verify=self._verify_ssl).json()
