import requests

BASE_URI = "http://js8:5000"


class Client:

    def __init__(self):
        self.url = BASE_URI
        self.session = requests.Session()
        self.auth_header = ''

    def set_auth_header(self, val):
        ''' set authorization header value'''
        self.auth_header = val

    def update(self, data, headers=None, query_params=None):
        """
        update the cockpit to the last version
        It is method for POST /cockpit/update
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/cockpit/update"
        return self.session.post(uri, data, headers=headers, params=query_params)

    def reloadAll(self, headers=None, query_params=None):
        """
        empty memory and reload all services
        It is method for GET /ays/reload
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/ays/reload"
        return self.session.get(uri, headers=headers, params=query_params)

    def addTemplateRepo(self, data, headers=None, query_params=None):
        """
        add a new service template repository
        It is method for POST /ays/template
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/ays/template"
        return self.session.post(uri, data, headers=headers, params=query_params)

    def listRepositories(self, headers=None, query_params=None):
        """
        list all repositorys
        It is method for GET /ays/repository
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/ays/repository"
        return self.session.get(uri, headers=headers, params=query_params)

    def createNewRepository(self, data, headers=None, query_params=None):
        """
        create a new repository
        It is method for POST /ays/repository
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/ays/repository"
        return self.session.post(uri, data, headers=headers, params=query_params)

    def getRepository(self, repository, headers=None, query_params=None):
        """
        Get information of a repository
        It is method for GET /ays/repository/{repository}
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/ays/repository/" + repository
        return self.session.get(uri, headers=headers, params=query_params)

    def deleteRepository(self, repository, headers=None, query_params=None):
        """
        Delete a repository
        It is method for DELETE /ays/repository/{repository}
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})
        repository = repository.split('/')[-1]
        uri = self.url + "/ays/repository/" + repository
        return self.session.delete(uri, headers=headers, params=query_params)

    def destroyRepository(self, repository, headers=None, query_params=None):
        """
        Destroy a repository
        It is method for POST /ays/repository/{repository}/destroy
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})
        repository = repository.split('/')[-1]
        uri = self.url + "/ays/repository/" + repository + "/destroy"
        return self.session.post(uri, headers=headers, params=query_params)

    def listBlueprints(self, repository, headers=None, query_params=None):
        """
        List all blueprint
        It is method for GET /ays/repository/{repository}/blueprint
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/ays/repository/" + repository + "/blueprint"
        return self.session.get(uri, headers=headers, params=query_params)

    def createNewBlueprint(self, data, repository, headers=None, query_params=None):
        """
        Create a new blueprint
        It is method for POST /ays/repository/{repository}/blueprint
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/ays/repository/" + repository + "/blueprint"
        return self.session.post(uri, data, headers=headers, params=query_params)

    def getBlueprint(self, blueprint, repository, headers=None, query_params=None):
        """
        Get a blueprint
        It is method for GET /ays/repository/{repository}/blueprint/{blueprint}
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/ays/repository/" + repository + "/blueprint/" + blueprint
        return self.session.get(uri, headers=headers, params=query_params)

    def executeBlueprint(self, data, blueprint, repository, headers=None, query_params=None):
        """
        Execute the blueprint
        It is method for POST /ays/repository/{repository}/blueprint/{blueprint}
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/ays/repository/" + repository + "/blueprint/" + blueprint
        return self.session.post(uri, data, headers=headers, params=query_params)

    def updateBlueprint(self, data, blueprint, repository, headers=None, query_params=None):
        """
        Update existing blueprint
        It is method for PUT /ays/repository/{repository}/blueprint/{blueprint}
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/ays/repository/" + repository + "/blueprint/" + blueprint
        return self.session.put(uri, data, headers=headers, params=query_params)

    def deleteBlueprint(self, blueprint, repository, headers=None, query_params=None):
        """
        delete blueprint
        It is method for DELETE /ays/repository/{repository}/blueprint/{blueprint}
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/ays/repository/" + repository + "/blueprint/" + blueprint
        return self.session.delete(uri, headers=headers, params=query_params)

    def archiveBlueprint(self, data, blueprint, repository, headers=None, query_params=None):
        """
        archive the blueprint
        It is method for PUT /ays/repository/{repository}/blueprint/{blueprint}/archive
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/ays/repository/" + repository + \
            "/blueprint/" + blueprint + "/archive"
        return self.session.put(uri, data, headers=headers, params=query_params)

    def restoreBlueprint(self, data, blueprint, repository, headers=None, query_params=None):
        """
        restore the blueprint
        It is method for PUT /ays/repository/{repository}/blueprint/{blueprint}/restore
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/ays/repository/" + repository + \
            "/blueprint/" + blueprint + "/restore"
        return self.session.put(uri, data, headers=headers, params=query_params)

    def listServices(self, repository, headers=None, query_params=None):
        """
        List all services in the repository
        It is method for GET /ays/repository/{repository}/service
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/ays/repository/" + repository + "/service"
        return self.session.get(uri, headers=headers, params=query_params)

    def listServicesByRole(self, role, repository, headers=None, query_params=None):
        """
        List all services of role 'role' in the repository
        It is method for GET /ays/repository/{repository}/service/{role}
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/ays/repository/" + repository + "/service/" + role
        return self.session.get(uri, headers=headers, params=query_params)

    def getServiceByName(self, name, role, repository, headers=None, query_params=None):
        """
        Get a service name
        It is method for GET /ays/repository/{repository}/service/{role}/{name}
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/ays/repository/" + repository + "/service/" + role + "/" + name
        return self.session.get(uri, headers=headers, params=query_params)

    def deleteServiceByName(self, name, role, repository, headers=None, query_params=None):
        """
        uninstall and delete a service
        It is method for DELETE /ays/repository/{repository}/service/{role}/{name}
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/ays/repository/" + \
            repository + "/service/" + role + "/" + name
        return self.session.delete(uri, headers=headers, params=query_params)

    def listServiceActions(self, instance, role, repository, headers=None, query_params=None):
        """
        Get list of action available on this service
        It is method for GET /ays/repository/{repository}/service/{role}/{instance}/action
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/ays/repository/" + repository + \
            "/service/" + role + "/" + instance + "/action"
        return self.session.get(uri, headers=headers, params=query_params)

    def listTemplates(self, repository, headers=None, query_params=None):
        """
        list all templates
        It is method for GET /ays/repository/{repository}/template
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/ays/repository/" + repository + "/template"
        return self.session.get(uri, headers=headers, params=query_params)

    def createNewTemplate(self, data, repository, headers=None, query_params=None):
        """
        Create new template
        It is method for POST /ays/repository/{repository}/template
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/ays/repository/" + repository + "/template"
        return self.session.post(uri, data, headers=headers, params=query_params)

    def updateTemplate(self, template, repository, headers=None, query_params=None):
        """
        update actor from template repo
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/ays/repository/" + repository + "/template/" + template + "/update"
        return self.session.get(uri, headers=headers, params=query_params)

    def updateTemplates(self, repository, headers=None, query_params=None):
        """
        update all actors in template repo
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/ays/repository/" + repository + "/template/" + "update"
        return self.session.get(uri, headers=headers, params=query_params)

    def getTemplate(self, template, repository, headers=None, query_params=None):
        """
        Get a template
        It is method for GET /ays/repository/{repository}/template/{template}
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/ays/repository/" + repository + "/template/" + template
        return self.session.get(uri, headers=headers, params=query_params)

    def listAYSTemplates(self, headers=None, query_params=None):
        """
        list all AYS templates on system
        it is a method for GET /ays/templates
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})
        uri = self.url + '/ays/templates'
        return self.session.get(uri, headers=headers, params=query_params)

    def getAYSTemplate(self, template, headers=None, query_params=None):
        """
        get an AYS template
        it is a method for GET /ays/template/{template}
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})
        uri = self.url + '/ays/templates/' + template
        return self.session.get(uri, headers=headers, params=query_params)

    def listActors(self, repository, headers=None, query_params=None):
        """
        list all actors in an ays repo
        It is method for GET /ays/repository/{repository}/actor
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})
        uri = self.url + '/ays/repository/' + repository + '/actor'
        return self.session.get(uri, headers=headers, params=query_params)

    def getActorByName(self, repository, actorname, headers=None, query_params=None):
        """
        list all actors in an ays repo
        It is method for GET /ays/repository/{repository}/actor/{actorname}
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})
        uri = self.url + '/ays/repository/' + repository + '/actor/' + actorname
        return self.session.get(uri, headers=headers, params=query_params)

    def listRuns(self, repository, headers=None, query_params=None):
        """
        list all runs of the repository
        It is method for GET /ays/repository/{repository}/aysrun
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/ays/repository/" + repository + "/aysrun"
        return self.session.get(uri, headers=headers, params=query_params)

    def getRun(self, aysrun, repository, headers=None, query_params=None):
        """
        Get an aysrun
        It is method for GET /ays/repository/{repository}/aysrun/{aysrun}
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/ays/repository/" + repository + "/aysrun/" + aysrun
        return self.session.get(uri, headers=headers, params=query_params)

    def createRun(self, data, repository, headers=None, query_params=None):
        """
        Create a run based on all the action scheduled
        It is method for POST /ays/repository/{repository}/aysrun
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/ays/repository/" + repository + "/aysrun"
        return self.session.post(uri, data, headers=headers, params=query_params)

    def webhooks_github_post(self, data, headers=None, query_params=None):
        """
        Endpoint that receives the events from github
        It is method for POST /webhooks/github
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/webhooks/github"
        return self.session.post(uri, data, headers=headers, params=query_params)

    def oauth_callback_get(self, headers=None, query_params=None):
        """
        oauth endpoint where oauth provider need to send authorization code
        It is method for GET /oauth/callback
        """
        if self.auth_header:
            self.session.headers.update({"Authorization": self.auth_header})

        uri = self.url + "/oauth/callback"
        return self.session.get(uri, headers=headers, params=query_params)
