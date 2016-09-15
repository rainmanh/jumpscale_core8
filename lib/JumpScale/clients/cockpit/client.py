import requests
from JumpScale.clients.cockpit.client_utils import build_query_string
from JumpScale.clients.cockpit import client_lower
from JumpScale import j


class ApiError(Exception):

    def __init__(self, response):
        msg = '%s %s' % (response.status_code, response.reason)
        try:
            message = response.json()['error']
        except:
            message = response.content
        if isinstance(message, (str, bytes)):
            msg += '\n%s' % message
        elif isinstance(message, dict) and 'errormessage' in message:
            msg += '\n%s' % message['errormessage']

        super(ApiError, self).__init__(msg)
        self._response = response

    @property
    def response(self):
        return self._response


class Client:
    """
    This client is the upper layer of the cockpit client.
    It uses the generated client from go-raml as backend.
    The backend client is not touch, this allow to re-generate the client
    without modifying the upper interface of the client.
    """

    def __init__(self, base_uri, jwt, verify_ssl=True):
        """
        base_uri: str, URL of the cockpit api. e.g: https://mycockpit.com/api
        jwt: str, json web token from itsyou.online
        """
        self._client = client_lower.Client()
        self._client.session.verify = verify_ssl
        if verify_ssl is False:
            requests.packages.urllib3.disable_warnings()
        self._client.url = base_uri
        self._jwt = jwt
        self._client.session.headers = {
            "Authorization": "Bearer " + jwt,
            "Content-Type": "application/json"
        }

    def _assert_response(self, resp, code=200):
        if resp.status_code != code:
            raise ApiError(resp)

        # 204 no-content, don't try to return anything
        if code == 204:
            return

        if resp.headers.get('content-type', 'text/html') == 'application/json':
            return resp.json()

        return resp.content

    def updateCockpit(self, headers=None, query_params=None):
        """
        update the cockpit to the last version
        It is method for POST /cockpit/update
        """
        resp = self._client.update(
            data=None, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def reloadAll(self, headers=None, query_params=None):
        """
        empty memory and reload all services
        It is method for GET /ays/reload
        """
        resp = self._client.reloadAll(
            headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def addTemplateRepo(self, url, branch, headers=None, query_params=None):
        """
        add a new service template repository
        It is method for POST /ays/template
        """
        data = j.data.serializer.json.dumps({
            'url': url,
            'branch': branch,
        })
        resp = self._client.addTemplateRepo(
            data=data, headers=headers, query_params=query_params)
        self._assert_response(resp, code=201)
        return resp.json()

    def listRepositories(self, headers=None, query_params=None):
        """
        list all repositorys
        It is method for GET /ays/repository
        """
        resp = self._client.listRepositories(
            headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def createNewRepository(self, name, headers=None, query_params=None):
        """
        create a new repository
        It is method for POST /ays/repository
        """
        data = j.data.serializer.json.dumps({'name': name})
        resp = self._client.createNewRepository(
            data=data, headers=headers, query_params=query_params)
        self._assert_response(resp, 201)
        return resp.json()

    def getRepository(self, repository, headers=None, query_params=None):
        """
        Get information of a repository
        It is method for GET /ays/repository/{repository}
        """
        resp = self._client.getRepository(
            repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def deleteRepository(self, repository, headers=None, query_params=None):
        """
        Delete a repository
        It is method for DELETE /ays/repository/{repository}
        """
        resp = self._client.deleteRepository(
            repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp, 204)
        return resp.json()

    def initRepository(self, repository, role='', instance='', force=False, headers=None, query_params=None):
        """
        Run init action on full repository
        It is method for POST /ays/repository/{repository}/init
        """
        query = {
            'role': role,
            'instance': instance,
        }
        query_params = query_params or {}
        query_params.update(query)

        resp = self._client.initRepository(
            repository=repository, data=None, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def simulateAction(self, repository, action, role='', instance='', producer_roles='*', force=False, headers=None, query_params=None):
        """
        simulate the execution of an action
        It is method for POST /ays/repository/{repository}/simulate
        """
        query = {
            'action': action,
            'role': role,
            'instance': instance,
            'producer_roles': producer_roles,
            'force': force,
        }
        query_params = query_params or {}
        query_params.update(query)

        resp = self._client.simulateAction(
            data=None, repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def executeAction(self, repository, action, role='', instance='', producer_roles='*', force=False, async=False, headers=None, query_params=None):
        """
        simulate the execution of an action
        It is method for POST /ays/repository/{repository}/simulate
        """
        query = {
            'action': action,
            'role': role,
            'instance': instance,
            'producer_roles': producer_roles,
            'force': force,
            'async': async,
        }
        query_params = query_params or {}
        query_params.update(query)

        resp = self._client.executeAction(
            data=None, repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def listBlueprints(self, repository, archived=True, headers=None, query_params=None):
        """
        List all blueprint
        It is method for GET /ays/repository/{repository}/blueprint
        archived: boolean, include archived blueprint or not
        """
        query = {'archived': archived}
        query_params = query_params or {}
        query_params.update(query)

        resp = self._client.listBlueprints(
            repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def createNewBlueprint(self, repository, name, content, headers=None, query_params=None):
        """
        Create a new blueprint
        It is method for POST /ays/repository/{repository}/blueprint
        """
        data = j.data.serializer.json.dumps({'name': name, 'content': content})
        resp = self._client.createNewBlueprint(
            data=data, repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp, 201)
        return resp.json()

    def getBlueprint(self, repository, blueprint, headers=None, query_params=None):
        """
        Get a blueprint
        It is method for GET /ays/repository/{repository}/blueprint/{blueprint}
        """
        resp = self._client.getBlueprint(
            blueprint=blueprint, repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def executeBlueprint(self, repository, blueprint, role='', instance='', headers=None, query_params=None):
        """
        Execute the blueprint
        It is method for POST /ays/repository/{repository}/blueprint/{blueprint}
        """
        query = {
            'role': role,
            'instance': instance,
        }
        query_params = query_params or {}
        query_params.update(query)

        resp = self._client.executeBlueprint(
            data=None, blueprint=blueprint, repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def updateBlueprint(self, repository, blueprint, content, headers=None, query_params=None):
        """
        Update existing blueprint
        It is method for PUT /ays/repository/{repository}/blueprint/{blueprint}
        """
        data = j.data.serializer.json.dumps(
            {'name': blueprint, 'content': content})
        resp = self._client.updateBlueprint(
            data=data, blueprint=blueprint, repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def deleteBlueprint(self, repository, blueprint, headers=None, query_params=None):
        """
        delete blueprint
        It is method for DELETE /ays/repository/{repository}/blueprint/{blueprint}
        """
        resp = self._client.deleteBlueprint(
            blueprint=blueprint, repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp, 204)
        return resp.json()

    def archiveBlueprint(self, repository, blueprint, headers=None, query_params=None):
        """
        archive blueprint
        It is method for PUT /ays/repository/{repository}/blueprint/{blueprint}/archive
        """
        resp = self._client.archiveBlueprint(
            data=None, blueprint=blueprint, repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def restoreBlueprint(self, repository, blueprint, headers=None, query_params=None):
        """
        archive blueprint
        It is method for PUT /ays/repository/{repository}/blueprint/{blueprint}/restore
        """
        resp = self._client.restoreBlueprint(
            data=None, blueprint=blueprint, repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def listServices(self, repository, headers=None, query_params=None):
        """
        List all services in the repository
        It is method for GET /ays/repository/{repository}/service
        """
        resp = self._client.listServices(
            repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def listServicesByRole(self, role, repository, headers=None, query_params=None):
        """
        List all services of role 'role' in the repository
        It is method for GET /ays/repository/{repository}/service/{role}
        """
        resp = self._client.listServicesByRole(
            role=role, repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def executeServiceActionByRole(self, action, role, repository, headers=None, query_params=None):
        """
        Perform an action on all service with the role 'role'
        It is method for POST /ays/repository/{repository}/service/{role}/action/{action}
        """
        resp = self._client.executeServiceActionByRole(
            data=None, action=action, role=role, repository=repository, headers=headers, query_params=query_params)
        resp.raise_for_status()
        return resp.json()

    def getServiceByInstance(self, instance, role, repository, headers=None, query_params=None):
        """
        Get a service instance
        It is method for GET /ays/repository/{repository}/service/{role}/{instance}
        """
        resp = self._client.getServiceByInstance(
            instance=instance, role=role, repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def deleteServiceByInstance(self, instance, role, repository, uninstall=False, headers=None, query_params=None):
        """
        uninstall and delete a service
        It is method for DELETE /ays/repository/{repository}/service/{role}/{instance}
        """
        query_params = query_params or {}
        query_params.update({'uninstall': uninstall})

        resp = self._client.deleteServiceByInstance(
            instance=instance, role=role, repository=repository, headers=headers, query_params=query_params)
        return self._assert_response(resp, 204)

    def listServiceActions(self, instance, role, repository, headers=None, query_params=None):
        """
        Get list of action available on this service
        It is method for GET /ays/repository/{repository}/service/{role}/{instance}/action
        """
        resp = self._client.listServiceActions(
            instance=instance, role=role, repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def executeServiceActionByInstance(self, action, instance, role, repository, headers=None, query_params=None):
        """
        Perform an action on a services
        It is method for POST /ays/repository/{repository}/service/{role}/{instance}/{action}
        """
        resp = self._client.executeServiceActionByInstance(
            data=None, action=action, instance=instance, role=role, repository=repository, headers=headers, query_params=query_params)
        resp.raise_for_status()
        return resp.json()

    def listTemplates(self, repository, headers=None, query_params=None):
        """
        list all templates
        It is method for GET /ays/repository/{repository}/template
        """
        resp = self._client.listTemplates(
            repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def createNewTemplate(self, repository, name, action, schema, headers=None, query_params=None):
        """
        Create new template
        It is method for POST /ays/repository/{repository}/template

        """
        data = j.data.serializer.json.dumps(
            {'name': 'myTemplate', 'action_py': 'valid action file', 'schema_hrd': 'valid hrd schema'})
        resp = self._client.createNewTemplate(
            data=data, repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp, 201)
        return resp.json()

    def getTemplate(self, template, repository, headers=None, query_params=None):
        """
        Get a template
        It is method for GET /ays/repository/{repository}/template/{template}
        """
        resp = self._client.getTemplate(
            template=template, repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def listRuns(self, repository, headers=None, query_params=None):
        """
        list all runs in the repository
        It is method for GET /ays/repository/{repository}/aysrun
        """
        resp = self._client.listRuns(
            repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def getRun(self, aysrun, repository, headers=None, query_params=None):
        """
        Get an aysrun
        It is method for GET /ays/repository/{repository}/aysrun/{aysrun}
        """
        resp = self._client.getRun(aysrun=aysrun, repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def getSource(self, source, repository, headers=None, query_params=None):
        """
        param:repository where source is
        param: hash hash of source file
        result json of source
        """
        resp = self._client.getSource(
            source=source, repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def getHRD(self, hrd, repository, headers=None, query_params=None):
        """
        param:repository where source is
        param: hash hash of hrd file
        result json of hrd
        """
        resp = self._client.getHRD(
            hrd=hrd, repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()
