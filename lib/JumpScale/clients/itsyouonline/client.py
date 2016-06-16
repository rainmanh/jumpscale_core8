import requests
from .client_utils import build_query_string

BASE_URI = "https://itsyou.online/api/"


class Client:
    def __init__(self):
        self.url = BASE_URI
        self.session = requests.Session()

    def CreateUser(self, data, headers=None, query_params=None):
        """
        Create a new user
        It is method for POST /users
        """
        uri = self.url + "/users"
        uri = uri + build_query_string(query_params)
        return self.session.post(uri, data, headers=headers)

    def GetNotifications(self, username, headers=None, query_params=None):
        """
        Get the list of notifications, these are pending invitations or approvals
        It is method for GET /users/{username}/notifications
        """
        uri = self.url + "/users/"+username+"/notifications"
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def GetUserOrganizations(self, username, headers=None, query_params=None):
        """
        Get the list organizations a user is owner or member of
        It is method for GET /users/{username}/organizations
        """
        uri = self.url + "/users/"+username+"/organizations"
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def AcceptMembership(self, data, globalid, role, username, headers=None, query_params=None):
        """
        Accept membership in organization
        It is method for POST /users/{username}/organizations/{globalid}/roles/{role}
        """
        uri = self.url + "/users/"+username+"/organizations/"+globalid+"/roles/"+role
        uri = uri + build_query_string(query_params)
        return self.session.post(uri, data, headers=headers)

    def users_byUsernameorganizations_byGlobalidrolesrole_delete(self, globalid, role, username, headers=None, query_params=None):
        """
        Reject membership invitation in an organization.
        It is method for DELETE /users/{username}/organizations/{globalid}/roles/{role}
        """
        uri = self.url + "/users/"+username+"/organizations/"+globalid+"/roles/"+role
        uri = uri + build_query_string(query_params)
        return self.session.delete(uri, headers=headers)

    def GetUser(self, username, headers=None, query_params=None):
        """
        It is method for GET /users/{username}
        """
        uri = self.url + "/users/"+username
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def UpdateUserName(self, data, username, headers=None, query_params=None):
        """
        Update the user his firstname and lastname
        It is method for PUT /users/{username}/name
        """
        uri = self.url + "/users/"+username+"/name"
        uri = uri + build_query_string(query_params)
        return self.session.put(uri, data, headers=headers)

    def UpdatePassword(self, data, username, headers=None, query_params=None):
        """
        Update the user his password
        It is method for PUT /users/{username}/password
        """
        uri = self.url + "/users/"+username+"/password"
        uri = uri + build_query_string(query_params)
        return self.session.put(uri, data, headers=headers)

    def GetEmailAddresses(self, username, headers=None, query_params=None):
        """
        Get a list of the user his email addresses.
        It is method for GET /users/{username}/emailaddresses
        """
        uri = self.url + "/users/"+username+"/emailaddresses"
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def RegisterNewEmailAddress(self, data, username, headers=None, query_params=None):
        """
        Register a new email address
        It is method for POST /users/{username}/emailaddresses
        """
        uri = self.url + "/users/"+username+"/emailaddresses"
        uri = uri + build_query_string(query_params)
        return self.session.post(uri, data, headers=headers)

    def UpdateEmailAddress(self, data, label, username, headers=None, query_params=None):
        """
        Updates the label and/or value of an email address
        It is method for PUT /users/{username}/emailaddresses/{label}
        """
        uri = self.url + "/users/"+username+"/emailaddresses/"+label
        uri = uri + build_query_string(query_params)
        return self.session.put(uri, data, headers=headers)

    def DeleteEmailAddress(self, label, username, headers=None, query_params=None):
        """
        Removes an email address
        It is method for DELETE /users/{username}/emailaddresses/{label}
        """
        uri = self.url + "/users/"+username+"/emailaddresses/"+label
        uri = uri + build_query_string(query_params)
        return self.session.delete(uri, headers=headers)

    def ValidateEmailAddress(self, data, label, username, headers=None, query_params=None):
        """
        Sends validation email to email address
        It is method for POST /users/{username}/emailaddresses/{label}/validate
        """
        uri = self.url + "/users/"+username+"/emailaddresses/"+label+"/validate"
        uri = uri + build_query_string(query_params)
        return self.session.post(uri, data, headers=headers)

    def ListAPIKeys(self, username, headers=None, query_params=None):
        """
        Lists the API keys
        It is method for GET /users/{username}/apikeys
        """
        uri = self.url + "/users/"+username+"/apikeys"
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def AddApiKey(self, data, username, headers=None, query_params=None):
        """
        Adds an APIKey to the user
        It is method for POST /users/{username}/apikeys
        """
        uri = self.url + "/users/"+username+"/apikeys"
        uri = uri + build_query_string(query_params)
        return self.session.post(uri, data, headers=headers)

    def GetAPIkey(self, label, username, headers=None, query_params=None):
        """
        Get an API key by label
        It is method for GET /users/{username}/apikeys/{label}
        """
        uri = self.url + "/users/"+username+"/apikeys/"+label
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def UpdateAPIkey(self, data, label, username, headers=None, query_params=None):
        """
        Updates the label for the api key
        It is method for PUT /users/{username}/apikeys/{label}
        """
        uri = self.url + "/users/"+username+"/apikeys/"+label
        uri = uri + build_query_string(query_params)
        return self.session.put(uri, data, headers=headers)

    def DeleteAPIkey(self, label, username, headers=None, query_params=None):
        """
        Removes an API key
        It is method for DELETE /users/{username}/apikeys/{label}
        """
        uri = self.url + "/users/"+username+"/apikeys/"+label
        uri = uri + build_query_string(query_params)
        return self.session.delete(uri, headers=headers)

    def DeleteGithubAccount(self, username, headers=None, query_params=None):
        """
        Unlink Github Account
        It is method for DELETE /users/{username}/github
        """
        uri = self.url + "/users/"+username+"/github"
        uri = uri + build_query_string(query_params)
        return self.session.delete(uri, headers=headers)

    def DeleteFacebookAccount(self, username, headers=None, query_params=None):
        """
        Delete the associated facebook account
        It is method for DELETE /users/{username}/facebook
        """
        uri = self.url + "/users/"+username+"/facebook"
        uri = uri + build_query_string(query_params)
        return self.session.delete(uri, headers=headers)

    def GetUserInformation(self, username, headers=None, query_params=None):
        """
        It is method for GET /users/{username}/info
        """
        uri = self.url + "/users/"+username+"/info"
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def users_byUsernamevalidate_get(self, username, headers=None, query_params=None):
        """
        It is method for GET /users/{username}/validate
        """
        uri = self.url + "/users/"+username+"/validate"
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def GetUserAddresses(self, username, headers=None, query_params=None):
        """
        It is method for GET /users/{username}/addresses
        """
        uri = self.url + "/users/"+username+"/addresses"
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def RegisterNewUserAddress(self, data, username, headers=None, query_params=None):
        """
        Register a new address
        It is method for POST /users/{username}/addresses
        """
        uri = self.url + "/users/"+username+"/addresses"
        uri = uri + build_query_string(query_params)
        return self.session.post(uri, data, headers=headers)

    def GetUserAddressByLabel(self, label, username, headers=None, query_params=None):
        """
        It is method for GET /users/{username}/addresses/{label}
        """
        uri = self.url + "/users/"+username+"/addresses/"+label
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def UpdateUserAddress(self, data, label, username, headers=None, query_params=None):
        """
        Update the label and/or value of an existing address.
        It is method for PUT /users/{username}/addresses/{label}
        """
        uri = self.url + "/users/"+username+"/addresses/"+label
        uri = uri + build_query_string(query_params)
        return self.session.put(uri, data, headers=headers)

    def DeleteUserAddress(self, label, username, headers=None, query_params=None):
        """
        Removes an address
        It is method for DELETE /users/{username}/addresses/{label}
        """
        uri = self.url + "/users/"+username+"/addresses/"+label
        uri = uri + build_query_string(query_params)
        return self.session.delete(uri, headers=headers)

    def GetUserBankAccounts(self, username, headers=None, query_params=None):
        """
        It is method for GET /users/{username}/banks
        """
        uri = self.url + "/users/"+username+"/banks"
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def CreateUserBankAccount(self, data, username, headers=None, query_params=None):
        """
        Create new bank account
        It is method for POST /users/{username}/banks
        """
        uri = self.url + "/users/"+username+"/banks"
        uri = uri + build_query_string(query_params)
        return self.session.post(uri, data, headers=headers)

    def GetUserBankAccountByLabel(self, username, label, headers=None, query_params=None):
        """
        It is method for GET /users/{username}/banks/{label}
        """
        uri = self.url + "/users/"+username+"/banks/"+label
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def UpdateUserBankAccount(self, data, username, label, headers=None, query_params=None):
        """
        Update an existing bankaccount and label.
        It is method for PUT /users/{username}/banks/{label}
        """
        uri = self.url + "/users/"+username+"/banks/"+label
        uri = uri + build_query_string(query_params)
        return self.session.put(uri, data, headers=headers)

    def users_byUsernamebankslabel_delete(self, username, label, headers=None, query_params=None):
        """
        Delete a BankAccount
        It is method for DELETE /users/{username}/banks/{label}
        """
        uri = self.url + "/users/"+username+"/banks/"+label
        uri = uri + build_query_string(query_params)
        return self.session.delete(uri, headers=headers)

    def GetUserPhoneNumbers(self, username, headers=None, query_params=None):
        """
        It is method for GET /users/{username}/phonenumbers
        """
        uri = self.url + "/users/"+username+"/phonenumbers"
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def RegisterNewUserPhonenumber(self, data, username, headers=None, query_params=None):
        """
        Register a new phonenumber
        It is method for POST /users/{username}/phonenumbers
        """
        uri = self.url + "/users/"+username+"/phonenumbers"
        uri = uri + build_query_string(query_params)
        return self.session.post(uri, data, headers=headers)

    def GetUserPhonenumberByLabel(self, label, username, headers=None, query_params=None):
        """
        It is method for GET /users/{username}/phonenumbers/{label}
        """
        uri = self.url + "/users/"+username+"/phonenumbers/"+label
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def UpdateUserPhonenumber(self, data, label, username, headers=None, query_params=None):
        """
        Update the label and/or value of an existing phonenumber.
        It is method for PUT /users/{username}/phonenumbers/{label}
        """
        uri = self.url + "/users/"+username+"/phonenumbers/"+label
        uri = uri + build_query_string(query_params)
        return self.session.put(uri, data, headers=headers)

    def DeleteUserPhonenumber(self, label, username, headers=None, query_params=None):
        """
        Removes a phonenumber
        It is method for DELETE /users/{username}/phonenumbers/{label}
        """
        uri = self.url + "/users/"+username+"/phonenumbers/"+label
        uri = uri + build_query_string(query_params)
        return self.session.delete(uri, headers=headers)

    def ValidatePhonenumber(self, data, label, username, headers=None, query_params=None):
        """
        Sends validation text to phone numbers
        It is method for POST /users/{username}/phonenumbers/{label}/activate
        """
        uri = self.url + "/users/"+username+"/phonenumbers/"+label+"/activate"
        uri = uri + build_query_string(query_params)
        return self.session.post(uri, data, headers=headers)

    def VerifyPhoneNumber(self, data, label, username, headers=None, query_params=None):
        """
        Verifies a phone number
        It is method for PUT /users/{username}/phonenumbers/{label}/activate
        """
        uri = self.url + "/users/"+username+"/phonenumbers/"+label+"/activate"
        uri = uri + build_query_string(query_params)
        return self.session.put(uri, data, headers=headers)

    def GetUserContracts(self, username, headers=None, query_params=None):
        """
        Get the contracts where the user is 1 of the parties. Order descending by date.
        It is method for GET /users/{username}/contracts
        """
        uri = self.url + "/users/"+username+"/contracts"
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def CreateUserContract(self, data, username, headers=None, query_params=None):
        """
        Create a new contract.
        It is method for POST /users/{username}/contracts
        """
        uri = self.url + "/users/"+username+"/contracts"
        uri = uri + build_query_string(query_params)
        return self.session.post(uri, data, headers=headers)

    def GetAllAuthorizations(self, username, headers=None, query_params=None):
        """
        Get the list of authorizations.
        It is method for GET /users/{username}/authorizations
        """
        uri = self.url + "/users/"+username+"/authorizations"
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def GetAuthorization(self, grantedTo, username, headers=None, query_params=None):
        """
        Get the authorization for a specific organization.
        It is method for GET /users/{username}/authorizations/{grantedTo}
        """
        uri = self.url + "/users/"+username+"/authorizations/"+grantedTo
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def UpdateAuthorization(self, data, grantedTo, username, headers=None, query_params=None):
        """
        Modify which information an organization is able to see.
        It is method for PUT /users/{username}/authorizations/{grantedTo}
        """
        uri = self.url + "/users/"+username+"/authorizations/"+grantedTo
        uri = uri + build_query_string(query_params)
        return self.session.put(uri, data, headers=headers)

    def DeleteAuthorization(self, grantedTo, username, headers=None, query_params=None):
        """
        Remove the authorization for an organization, the granted organization will no longer have access the user's information.
        It is method for DELETE /users/{username}/authorizations/{grantedTo}
        """
        uri = self.url + "/users/"+username+"/authorizations/"+grantedTo
        uri = uri + build_query_string(query_params)
        return self.session.delete(uri, headers=headers)

    def CreateNewOrganization(self, data, headers=None, query_params=None):
        """
        Create a new organization. 1 user should be in the owners list. Validation is performed to check if the securityScheme allows management on this user.
        It is method for POST /organizations
        """
        uri = self.url + "/organizations"
        uri = uri + build_query_string(query_params)
        return self.session.post(uri, data, headers=headers)

    def GetOrganization(self, globalid, headers=None, query_params=None):
        """
        Get organization info
        It is method for GET /organizations/{globalid}
        """
        uri = self.url + "/organizations/"+globalid
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def CreateNewSubOrganization(self, data, globalid, headers=None, query_params=None):
        """
        Create a new suborganization.
        It is method for POST /organizations/{globalid}
        """
        uri = self.url + "/organizations/"+globalid
        uri = uri + build_query_string(query_params)
        return self.session.post(uri, data, headers=headers)

    def UpdateOrganization(self, data, globalid, headers=None, query_params=None):
        """
        Update organization info
        It is method for PUT /organizations/{globalid}
        """
        uri = self.url + "/organizations/"+globalid
        uri = uri + build_query_string(query_params)
        return self.session.put(uri, data, headers=headers)

    def GetOrganizationTree(self, globalid, headers=None, query_params=None):
        """
        It is method for GET /organizations/{globalid}/tree
        """
        uri = self.url + "/organizations/"+globalid+"/tree"
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def AddOrganizationMember(self, data, globalid, headers=None, query_params=None):
        """
        Assign a member to organization.
        It is method for POST /organizations/{globalid}/members
        """
        uri = self.url + "/organizations/"+globalid+"/members"
        uri = uri + build_query_string(query_params)
        return self.session.post(uri, data, headers=headers)

    def RemoveOrganizationMember(self, username, globalid, headers=None, query_params=None):
        """
        Remove a member from organization
        It is method for DELETE /organizations/{globalid}/members/{username}
        """
        uri = self.url + "/organizations/"+globalid+"/members/"+username
        uri = uri + build_query_string(query_params)
        return self.session.delete(uri, headers=headers)

    def AddOrganizationOwner(self, data, globalid, headers=None, query_params=None):
        """
        Invite a user to become owner of an organization.
        It is method for POST /organizations/{globalid}/owners
        """
        uri = self.url + "/organizations/"+globalid+"/owners"
        uri = uri + build_query_string(query_params)
        return self.session.post(uri, data, headers=headers)

    def RemoveOrganizationOwner(self, username, globalid, headers=None, query_params=None):
        """
        Remove an owner from organization
        It is method for DELETE /organizations/{globalid}/owners/{username}
        """
        uri = self.url + "/organizations/"+globalid+"/owners/"+username
        uri = uri + build_query_string(query_params)
        return self.session.delete(uri, headers=headers)

    def GetOrganizationContracts(self, globalid, headers=None, query_params=None):
        """
        Get the contracts where the organization is 1 of the parties. Order descending by date.
        It is method for GET /organizations/{globalid}/contracts
        """
        uri = self.url + "/organizations/"+globalid+"/contracts"
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def CreateOrganizationContracty(self, data, globalid, headers=None, query_params=None):
        """
        Create a new contract.
        It is method for POST /organizations/{globalid}/contracts
        """
        uri = self.url + "/organizations/"+globalid+"/contracts"
        uri = uri + build_query_string(query_params)
        return self.session.post(uri, data, headers=headers)

    def GetPendingOrganizationInvitations(self, globalid, headers=None, query_params=None):
        """
        Get the list of pending invitations for users to join this organization.
        It is method for GET /organizations/{globalid}/invitations
        """
        uri = self.url + "/organizations/"+globalid+"/invitations"
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def RemovePendingOrganizationInvitation(self, username, globalid, headers=None, query_params=None):
        """
        Cancel a pending invitation.
        It is method for DELETE /organizations/{globalid}/invitations/{username}
        """
        uri = self.url + "/organizations/"+globalid+"/invitations/"+username
        uri = uri + build_query_string(query_params)
        return self.session.delete(uri, headers=headers)

    def GetOrganizationAPIKeyLabels(self, globalid, headers=None, query_params=None):
        """
        Get the list of active api keys.
        It is method for GET /organizations/{globalid}/apikeys
        """
        uri = self.url + "/organizations/"+globalid+"/apikeys"
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def CreateNewOrganizationAPIKey(self, data, globalid, headers=None, query_params=None):
        """
        Create a new API Key, a secret itself should not be provided, it will be generated serverside.
        It is method for POST /organizations/{globalid}/apikeys
        """
        uri = self.url + "/organizations/"+globalid+"/apikeys"
        uri = uri + build_query_string(query_params)
        return self.session.post(uri, data, headers=headers)

    def GetOrganizationAPIKey(self, label, globalid, headers=None, query_params=None):
        """
        It is method for GET /organizations/{globalid}/apikeys/{label}
        """
        uri = self.url + "/organizations/"+globalid+"/apikeys/"+label
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def UpdateOrganizationAPIKey(self, data, label, globalid, headers=None, query_params=None):
        """
        Updates the label or other properties of a key.
        It is method for PUT /organizations/{globalid}/apikeys/{label}
        """
        uri = self.url + "/organizations/"+globalid+"/apikeys/"+label
        uri = uri + build_query_string(query_params)
        return self.session.put(uri, data, headers=headers)

    def DeleteOrganizationAPIKey(self, label, globalid, headers=None, query_params=None):
        """
        Removes an API key
        It is method for DELETE /organizations/{globalid}/apikeys/{label}
        """
        uri = self.url + "/organizations/"+globalid+"/apikeys/"+label
        uri = uri + build_query_string(query_params)
        return self.session.delete(uri, headers=headers)

    def CreateOrganizationDNS(self, data, dnsname, globalid, headers=None, query_params=None):
        """
        Creates a new DNS name associated with an organization
        It is method for POST /organizations/{globalid}/dns/{dnsname}
        """
        uri = self.url + "/organizations/"+globalid+"/dns/"+dnsname
        uri = uri + build_query_string(query_params)
        return self.session.post(uri, data, headers=headers)

    def UpdateOrganizationDNS(self, data, dnsname, globalid, headers=None, query_params=None):
        """
        Updates an existing DNS name associated with an organization
        It is method for PUT /organizations/{globalid}/dns/{dnsname}
        """
        uri = self.url + "/organizations/"+globalid+"/dns/"+dnsname
        uri = uri + build_query_string(query_params)
        return self.session.put(uri, data, headers=headers)

    def DeleteOrganizaitonDNS(self, dnsname, globalid, headers=None, query_params=None):
        """
        Removes a DNS name
        It is method for DELETE /organizations/{globalid}/dns/{dnsname}
        """
        uri = self.url + "/organizations/"+globalid+"/dns/"+dnsname
        uri = uri + build_query_string(query_params)
        return self.session.delete(uri, headers=headers)

    def GetCompanyList(self, headers=None, query_params=None):
        """
        Get companies. Authorization limits are applied to requesting user.
        It is method for GET /companies
        """
        uri = self.url + "/companies"
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def CreateCompany(self, data, headers=None, query_params=None):
        """
        Register a new company
        It is method for POST /companies
        """
        uri = self.url + "/companies"
        uri = uri + build_query_string(query_params)
        return self.session.post(uri, data, headers=headers)

    def GetCompany(self, globalId, headers=None, query_params=None):
        """
        Get organization info
        It is method for GET /companies/{globalId}
        """
        uri = self.url + "/companies/"+globalId
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def UpdateCompany(self, data, globalId, headers=None, query_params=None):
        """
        Update existing company. Updating ``globalId`` is not allowed.
        It is method for PUT /companies/{globalId}
        """
        uri = self.url + "/companies/"+globalId
        uri = uri + build_query_string(query_params)
        return self.session.put(uri, data, headers=headers)

    def GetCompanyContracts(self, globalId, headers=None, query_params=None):
        """
        Get the contracts where the organization is 1 of the parties. Order descending by date.
        It is method for GET /companies/{globalId}/contracts
        """
        uri = self.url + "/companies/"+globalId+"/contracts"
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def CreateCompanyContract(self, data, globalId, headers=None, query_params=None):
        """
        Create a new contract.
        It is method for POST /companies/{globalId}/contracts
        """
        uri = self.url + "/companies/"+globalId+"/contracts"
        uri = uri + build_query_string(query_params)
        return self.session.post(uri, data, headers=headers)

    def GetCompanyInfo(self, globalId, headers=None, query_params=None):
        """
        It is method for GET /companies/{globalId}/info
        """
        uri = self.url + "/companies/"+globalId+"/info"
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def companies_byGlobalId_validate_get(self, globalId, headers=None, query_params=None):
        """
        It is method for GET /companies/{globalId}/validate
        """
        uri = self.url + "/companies/"+globalId+"/validate"
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def GetContract(self, contractId, headers=None, query_params=None):
        """
        Get a contract
        It is method for GET /contracts/{contractId}
        """
        uri = self.url + "/contracts/"+contractId
        uri = uri + build_query_string(query_params)
        return self.session.get(uri, headers=headers)

    def SignContract(self, data, contractId, headers=None, query_params=None):
        """
        Sign a contract
        It is method for POST /contracts/{contractId}/signatures
        """
        uri = self.url + "/contracts/"+contractId+"/signatures"
        uri = uri + build_query_string(query_params)
        return self.session.post(uri, data, headers=headers)
