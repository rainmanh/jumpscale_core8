from JumpScale import j


class GogsClient(object):

    def __init__(self, addr,port,login,passwd): 
        self._client=...
        #@todo (*1*) use requests lib to go to rest interface of gogs
        #https://github.com/gogits/gogs/tree/master/routers/api/v1
        #https://github.com/gogits/go-gogs-client/wiki
        #modify gogs if have to to get API to do what we want (seems to be incomplete)


    def organization_create(self,name):

    def organization_delete(self,name):

    def organizations_user_add(self,orgname,username,access="RW"):
        """
        ...

        """

    def organizations_user_delete(self,orgname,username):

    def organizations_list(self):
        """
        return 
        ...
        """

    def organization_get():
        """
        return detailed info as json is ok (result of api call)
        """



    def user_set(self,name,email,pubkey):
        """
        if user exists then will just set the email & pubkey
        """

    def user_delete(self,name):

    def users_list(self):

    def user_get():
        """
        return detailed info as json is ok (result of api call)
        """


    def repository_create(self,organization,name,description="",private=True,readme=True):

    def repository_delete(self,organization,name):

    def repository_delete(self,organization,name):

    def repositories_get(self):
        """
        return list of all repositories
        return 
        [[$id,$name,$ssh_url]]
        """

    def repository_user_add(self,name,username,access="RW"):
        """
        make sure a user can access the repository

        """

    def repository_get():
        """
        return detailed info as json is ok (result of api call)
        """

    def repository_user_delete(self,name,username):


    def issues_list

    def issue_get

    def issue_create


    def issue_delete


    ...