from JumpScale import j
import requests
from requests.auth import HTTPBasicAuth
from random import randint


class GogsBaseException(Exception):
    pass


class AdminRequiredException(GogsBaseException):
    pass


class DataErrorException(GogsBaseException):
    pass


class NotFoundException(GogsBaseException):
    pass

class GogsServerErrorException(GogsBaseException):
    pass


class GogsClient(object):
    """
    some depend on an edited gogs , which is not yet pushed 
    """

    def __init__(self, addr, port, login, passwd):
        self.addr = addr
        self.port = port
        self._login = login
        self._passwd = passwd
        self.base_url = "%s:%s/api/v1" % (addr, port)

        self.session = requests.session()
        self.session.auth = HTTPBasicAuth(login, passwd)
        #@todo (*1*) use requests lib to go to rest interface of gogs
        # https://github.com/gogits/gogs/tree/master/routers/api/v1
        # https://github.com/gogits/go-gogs-client/wiki
        # modify gogs if have to to get API to do what we want (seems to be
        # incomplete)

    def organization_create(self, name, full_name=None, description=None, website=None, location=None):
        pass
        """
        create an organization by user with name 
        """
        if not full_name:
            full_name = name

        body = {
            "username": name,
            "full_name": full_name,
            "description": description,
            "website": website,
            "location": location
        }
        try:
            self.organization_get(name)
            response_set = self.session.patch('%s/admin/users/%s/orgs/' % (self.base_url, self._login), data=body)
        except NotFoundException:
            response_set = self.session.post('%s/admin/users' % (self.base_url), data=body)

        if response_set.status_code == 201:
            return response_set.json()
        elif response_set.status_code == 422:
            raise DataErrorException("%s is required or already exists"%response_set.json()['message'])
        elif response_set.status_code == 403:
            raise AdminRequiredException('Admin access Required')


    def organization_delete(self, org_name):
        """
        delete organization 
        """
        response_delete = self.session.delete('%s/admin/users/%s/orgs/%s'%(self.base_url, self._login, org_name))
        if response_delete.status_code == 204:
            return True
        elif response_delete.status_code == 403:
            raise AdminRequiredException('Admin access Required')
        else:
            raise NotFoundException()



    def organizations_user_add(self, orgname, username, access="RW"):
        pass
        # """
        # ...

        # """

    def organizations_user_delete(self, orgname, username):
        pass

    def organizations_list(self, user_name=None):
        """
        list organizations of current user         
        """
        if not user_name:
            response_orgs = self.session.get('%s/user/orgs'%(self.base_url))
        else:
            response_orgs = self.session.get('%s/users/%s/orgs'%(self.base_url, user_name))
        if response_orgs.status_code == 200:
            return response_orgs.json()


    def organization_get(self, org_name=None):
        """
        return detailed info as json is ok (result of api call)
        """
        if not org_name:
            return self.organizations_list()
        response_org = self.session.get('%s/orgs/%s' % (self.base_url, org_name))
        import ipdb;ipdb.set_trace()
        if response_org.status_code == 200:
            return response_org.json()
        else:
            raise GogsBaseException()


    def user_set(self, name, email, pubkey=None, **args):
        """
        creates user, if user exists then will just set the email & pubkey
        """
        body = {
            "login_name": name,
            "username": name,
            "email": email
        }
        def pubkey_name():
            pubkey_name = 'pubkey%d'%(randint(1, 100))
            response_exists = self.session.get('%s/user/keys/%s'%(self.base_url, pubkey_name))
            if response_exists.status_code == 404:
                return pubkey_name
            else:
                pubkey_name()

        if pubkey:
            data = {"title": pubkey_name(), "key": pubkey}
            response_pubk = self.session.post('%s/user/keys/'%(self.base_url), data=data)
            if response_pubk.status_code == 422:
                raise DataErrorException('pubkey exists or is invalid')

        try:
            self.user_get(name)
            response_set = self.session.patch('%s/admin/users/%s' % (self.base_url, name), data=body)
        except NotFoundException:
            response_set = self.session.post('%s/admin/users' % (self.base_url), data=body)

        if response_set.status_code == 201:
            return True
        elif response_set.status_code == 422:
            raise DataErrorException("%s is required or already exists"%response_set.json()['message'])
        elif response_set.status_code == 403:
            raise AdminRequiredException('Admin access Required')

    def user_delete(self, name):
        """
        deletes a user with provided username   
        """

        response_delete = self.session.delete('%s/admin/users/%s'%(self.base_url, name))
        if response_delete.status_code == 204:
            return True
        elif response_delete.status_code == 403:
            raise AdminRequiredException('Admin access Required')
        else:
            raise NotFoundException()

    def users_list(self, page=1, limit=10):
        pass
        """
        returns a json that lists the users , accesible from admin accounts
        """
        response_list = self.session.get('%s/admin/users/'%(self.base_url), params={'page': page, "limit": limit})        
        
        if response_list.status_code == 200:
            return response_list.json()
        elif response_list.status_code == 500:
            raise GogsServerErrorException()


    def user_get(self, name=None):
        """
        return detailed info as json is ok (result of api call)
        """
        if not name:
            name = self._login

        response_user = self.session.get('%s/users/%s'%(self.base_url, name))
        if response_user.status_code == 200:
            return response_user.json()
        else:
            raise NotFoundException()

    def repository_create(self, organization, name, description="", private=True, readme=True):
        """
        create repository using specified username 
        """
        body = {
            "name": name,
            "description": description,
            "private": private,
            "readme": "default"
                }

        response_set = self.session.post('%s/user/repos'%(self.base_url), data=body)
        if response_set.status_code == 200:
            return response_set.json()
        elif response_set.status_code == 422:
            raise DataErrorException("%s is required or already exists"%response_set.json()['message'])
        elif response_set.status_code == 403:
            raise AdminRequiredException('Admin access Required')



    def repository_delete(self, organization, name):
        """
        deletes a repository
        """
        response_delete = self.session.delete('%s/repos/%s/%s' % (self.base_url, self._login, name))
        if response_delete.status_code == 204:
            return True
        elif response_delete.status_code == 403:
            raise AdminRequiredException('loged in user is a owner of the repository')
        else:
            raise NotFoundException()


    def repositories_get(self):
        """
        return list of all repositories
        return
        [[$id,$name,$ssh_url]]
        """
        repos = list()
        response_repos = self.session.get('%s/user/repos' % (self.base_url))
        if response_repos.status_code == 200:
            for repo in response_repos.json['data']:
                repos.append([repo['id'], repo['full_name'], repo['ssh_url']])
            return repos
        else:
            raise GogsBaseException()

    def repository_user_add(self, name, username, access="RW"):
        pass
        # """
        # make sure a user can access the repository

        # """

    def repository_get(self, repo_name, user_name=None):
        """
        return detailed info as json is ok (result of api call)
        """
        if not user_name:
            user_name = self._login

        response_user = self.session.get('%s/repos/%s/%s'%(self.base_url, user_name, repo_name))
        if response_user.status_code == 200:
            return response_user.json()
        else:
            raise NotFoundException("User or repo does not exist")


    def repository_user_delete(self, name, username):
        pass

    def issues_list():
        pass

    def issue_get():
        pass

    def issue_create():
        pass

    def issue_delete():
        pass
