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

    def __init__(self, base_uri, jwt=None, verify_ssl=True):
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

    def createNewRepository(self, name, git_url, headers=None, query_params=None):
        """
        create a new repository
        It is method for POST /ays/repository
        """
        data = j.data.serializer.json.dumps({'name': name, 'git_url': git_url})
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

    def deleteRepository(self, repository, headers=None, query_params=None):
        """
        Delete a repository
        It is method for POST /ays/repository/{repository}/destroy
        """
        resp = self._client.deleteRepository(
            repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp, 204)

    def simulateAction(self, repository, action, role='', instance='',
                       producer_roles='*', force=False, headers=None, query_params=None):
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

    def executeAction(self, repository, action, role='', instance='', producer_roles='*', headers=None, query_params=None):
        """
        simulate the execution of an action
        It is method for POST /ays/repository/{repository}/simulate
        """
        query = {
            'action': action,
            'role': role,
            'instance': instance,
            'producer_roles': producer_roles,
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
        data = j.data.serializer.json.dumps({'name': blueprint, 'content': content})
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

    def listServicesByRole(self, repository, role, headers=None, query_params=None):
        """
        List all services of role 'role' in the repository
        It is method for GET /ays/repository/{repository}/service/{role}
        """
        resp = self._client.listServicesByRole(
            role=role, repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def getServiceByName(self, repository, role, name, headers=None, query_params=None):
        """
        Get a service by it's name
        It is method for GET /ays/repository/{repository}/service/{role}/{instance}
        """
        resp = self._client.getServiceByName(
            name=name, role=role, repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def deleteServiceByName(self,repository, role, name, headers=None, query_params=None):
        """
        uninstall and delete a service
        It is method for DELETE /ays/repository/{repository}/service/{role}/{name}
        """
        resp = self._client.deleteServiceByName(
            name=name, role=role, repository=repository, headers=headers, query_params=query_params)
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

    def listTemplates(self, repository, headers=None, query_params=None):
        """
        list all templates
        It is method for GET /ays/repository/{repository}/template
        """
        resp = self._client.listTemplates(
            repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def listAYSTemplates(self, headers=None, query_params=None):
        """
        list all templates from ays_jumpscale
        It is a method for GET /ays/templates
        """
        resp = self._client.listAYSTemplates(headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def getAYSTemplate(self, template, headers=None, query_params=None):
        """
        get template from ays_jumpscale
        It is a method for GET /ays/template/{template}
        """
        resp = self._client.getAYSTemplate(template, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def listActors(self, repository, headers=None, query_params=None):
        """
        list all actors in ays repo
        it is a method for GET /ays/repository/{repository}/actor
        """
        resp = self._client.listActors(repository, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def getActorByName(self, repository, actorname, headers=None, query_params=None):
        """
        list all actors in ays repo
        it is a method for GET /ays/repository/{repository}/actor/{actorname}
        """
        resp = self._client.getActorByName(repository, actorname, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def updateTemplate(self, repository, template=None,  headers=None, query_params=None):
        """
        update template in repo
        It is method for GET /ays/repository/{repository}/template/{template}/update
        """
        resp = self._client.updateTemplate(
            template=template, repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def updateTemplates(self, repository, headers=None, query_params=None):
        """
        update all templates in repo
        It is method for GET /ays/repository/{repository}/template/update
        """
        resp = self._client.updateTemplates(
            repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def getTemplate(self, repository, template, headers=None, query_params=None):
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

    def getRun(self, repository, aysrun, headers=None, query_params=None):
        """
        Get an aysrun
        It is method for GET /ays/repository/{repository}/aysrun/{aysrun}
        """
        resp = self._client.getRun(
            aysrun=aysrun, repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()

    def createRun(self, repository, callback_url=None, simulate=False,  headers=None, query_params=None):
        query = {
            'simulate': simulate,
            'callback_url': callback_url
        }
        query_params = query_params or {}
        query_params.update(query)

        resp = self._client.createRun(data=None, repository=repository, headers=headers, query_params=query_params)
        self._assert_response(resp)
        return resp.json()
