class UsersService:
    def __init__(self, client):
        self.client = client



    def CreateUser(self, data, headers=None, query_params=None):
        """
        Create a new user
        It is method for POST /users
        """
        uri = self.client.base_url + "/users"
        return self.client.post(uri, data, headers=headers, params=query_params)


    def GetUser(self, username, headers=None, query_params=None):
        """
        It is method for GET /users/{username}
        """
        uri = self.client.base_url + "/users/"+username
        return self.client.session.get(uri, headers=headers, params=query_params)


    def RegisterNewUserAddress(self, data, username, headers=None, query_params=None):
        """
        Register a new address
        It is method for POST /users/{username}/addresses
        """
        uri = self.client.base_url + "/users/"+username+"/addresses"
        return self.client.post(uri, data, headers=headers, params=query_params)


    def GetUserAddresses(self, username, headers=None, query_params=None):
        """
        It is method for GET /users/{username}/addresses
        """
        uri = self.client.base_url + "/users/"+username+"/addresses"
        return self.client.session.get(uri, headers=headers, params=query_params)


    def GetUserAddressByLabel(self, label, username, headers=None, query_params=None):
        """
        It is method for GET /users/{username}/addresses/{label}
        """
        uri = self.client.base_url + "/users/"+username+"/addresses/"+label
        return self.client.session.get(uri, headers=headers, params=query_params)


    def UpdateUserAddress(self, data, label, username, headers=None, query_params=None):
        """
        Update the label and/or value of an existing address.
        It is method for PUT /users/{username}/addresses/{label}
        """
        uri = self.client.base_url + "/users/"+username+"/addresses/"+label
        return self.client.put(uri, data, headers=headers, params=query_params)


    def DeleteUserAddress(self, label, username, headers=None, query_params=None):
        """
        Removes an address
        It is method for DELETE /users/{username}/addresses/{label}
        """
        uri = self.client.base_url + "/users/"+username+"/addresses/"+label
        return self.client.session.delete(uri, headers=headers, params=query_params)


    def AddApiKey(self, data, username, headers=None, query_params=None):
        """
        Adds an APIKey to the user
        It is method for POST /users/{username}/apikeys
        """
        uri = self.client.base_url + "/users/"+username+"/apikeys"
        return self.client.post(uri, data, headers=headers, params=query_params)


    def ListAPIKeys(self, username, headers=None, query_params=None):
        """
        Lists the API keys
        It is method for GET /users/{username}/apikeys
        """
        uri = self.client.base_url + "/users/"+username+"/apikeys"
        return self.client.session.get(uri, headers=headers, params=query_params)


    def DeleteAPIkey(self, label, username, headers=None, query_params=None):
        """
        Removes an API key
        It is method for DELETE /users/{username}/apikeys/{label}
        """
        uri = self.client.base_url + "/users/"+username+"/apikeys/"+label
        return self.client.session.delete(uri, headers=headers, params=query_params)


    def UpdateAPIkey(self, data, label, username, headers=None, query_params=None):
        """
        Updates the label for the api key
        It is method for PUT /users/{username}/apikeys/{label}
        """
        uri = self.client.base_url + "/users/"+username+"/apikeys/"+label
        return self.client.put(uri, data, headers=headers, params=query_params)


    def GetAPIkey(self, label, username, headers=None, query_params=None):
        """
        Get an API key by label
        It is method for GET /users/{username}/apikeys/{label}
        """
        uri = self.client.base_url + "/users/"+username+"/apikeys/"+label
        return self.client.session.get(uri, headers=headers, params=query_params)


    def GetAllAuthorizations(self, username, headers=None, query_params=None):
        """
        Get the list of authorizations.
        It is method for GET /users/{username}/authorizations
        """
        uri = self.client.base_url + "/users/"+username+"/authorizations"
        return self.client.session.get(uri, headers=headers, params=query_params)


    def UpdateAuthorization(self, data, grantedTo, username, headers=None, query_params=None):
        """
        Modify which information an organization is able to see.
        It is method for PUT /users/{username}/authorizations/{grantedTo}
        """
        uri = self.client.base_url + "/users/"+username+"/authorizations/"+grantedTo
        return self.client.put(uri, data, headers=headers, params=query_params)


    def GetAuthorization(self, grantedTo, username, headers=None, query_params=None):
        """
        Get the authorization for a specific organization.
        It is method for GET /users/{username}/authorizations/{grantedTo}
        """
        uri = self.client.base_url + "/users/"+username+"/authorizations/"+grantedTo
        return self.client.session.get(uri, headers=headers, params=query_params)


    def DeleteAuthorization(self, grantedTo, username, headers=None, query_params=None):
        """
        Remove the authorization for an organization, the granted organization will no longer have access the user's information.
        It is method for DELETE /users/{username}/authorizations/{grantedTo}
        """
        uri = self.client.base_url + "/users/"+username+"/authorizations/"+grantedTo
        return self.client.session.delete(uri, headers=headers, params=query_params)


    def CreateUserBankAccount(self, data, username, headers=None, query_params=None):
        """
        Create new bank account
        It is method for POST /users/{username}/banks
        """
        uri = self.client.base_url + "/users/"+username+"/banks"
        return self.client.post(uri, data, headers=headers, params=query_params)


    def GetUserBankAccounts(self, username, headers=None, query_params=None):
        """
        It is method for GET /users/{username}/banks
        """
        uri = self.client.base_url + "/users/"+username+"/banks"
        return self.client.session.get(uri, headers=headers, params=query_params)


    def GetUserBankAccountByLabel(self, username, label, headers=None, query_params=None):
        """
        It is method for GET /users/{username}/banks/{label}
        """
        uri = self.client.base_url + "/users/"+username+"/banks/"+label
        return self.client.session.get(uri, headers=headers, params=query_params)


    def UpdateUserBankAccount(self, data, username, label, headers=None, query_params=None):
        """
        Update an existing bankaccount and label.
        It is method for PUT /users/{username}/banks/{label}
        """
        uri = self.client.base_url + "/users/"+username+"/banks/"+label
        return self.client.put(uri, data, headers=headers, params=query_params)


    def DeleteUserBankAccount(self, username, label, headers=None, query_params=None):
        """
        Delete a BankAccount
        It is method for DELETE /users/{username}/banks/{label}
        """
        uri = self.client.base_url + "/users/"+username+"/banks/"+label
        return self.client.session.delete(uri, headers=headers, params=query_params)


    def CreateUserContract(self, data, username, headers=None, query_params=None):
        """
        Create a new contract.
        It is method for POST /users/{username}/contracts
        """
        uri = self.client.base_url + "/users/"+username+"/contracts"
        return self.client.post(uri, data, headers=headers, params=query_params)


    def GetUserContracts(self, username, headers=None, query_params=None):
        """
        Get the contracts where the user is 1 of the parties. Order descending by date.
        It is method for GET /users/{username}/contracts
        """
        uri = self.client.base_url + "/users/"+username+"/contracts"
        return self.client.session.get(uri, headers=headers, params=query_params)


    def GetDigitalWallet(self, username, headers=None, query_params=None):
        """
        It is method for GET /users/{username}/digitalwallet
        """
        uri = self.client.base_url + "/users/"+username+"/digitalwallet"
        return self.client.session.get(uri, headers=headers, params=query_params)


    def RegisterNewDigitalAssetAddress(self, data, username, headers=None, query_params=None):
        """
        Register a new digital asset address
        It is method for POST /users/{username}/digitalwallet
        """
        uri = self.client.base_url + "/users/"+username+"/digitalwallet"
        return self.client.post(uri, data, headers=headers, params=query_params)


    def UpdateDigitalAssetAddress(self, data, label, username, headers=None, query_params=None):
        """
        Update the label and/or value of an existing address.
        It is method for PUT /users/{username}/digitalwallet/{label}
        """
        uri = self.client.base_url + "/users/"+username+"/digitalwallet/"+label
        return self.client.put(uri, data, headers=headers, params=query_params)


    def GetDigitalAssetAddressByLabel(self, label, username, headers=None, query_params=None):
        """
        It is method for GET /users/{username}/digitalwallet/{label}
        """
        uri = self.client.base_url + "/users/"+username+"/digitalwallet/"+label
        return self.client.session.get(uri, headers=headers, params=query_params)


    def DeleteDigitalAssetAddress(self, label, username, headers=None, query_params=None):
        """
        Removes an address
        It is method for DELETE /users/{username}/digitalwallet/{label}
        """
        uri = self.client.base_url + "/users/"+username+"/digitalwallet/"+label
        return self.client.session.delete(uri, headers=headers, params=query_params)


    def GetEmailAddresses(self, username, headers=None, query_params=None):
        """
        Get a list of the user his email addresses.
        It is method for GET /users/{username}/emailaddresses
        """
        uri = self.client.base_url + "/users/"+username+"/emailaddresses"
        return self.client.session.get(uri, headers=headers, params=query_params)


    def RegisterNewEmailAddress(self, data, username, headers=None, query_params=None):
        """
        Register a new email address
        It is method for POST /users/{username}/emailaddresses
        """
        uri = self.client.base_url + "/users/"+username+"/emailaddresses"
        return self.client.post(uri, data, headers=headers, params=query_params)


    def UpdateEmailAddress(self, data, label, username, headers=None, query_params=None):
        """
        Updates the label and/or value of an email address
        It is method for PUT /users/{username}/emailaddresses/{label}
        """
        uri = self.client.base_url + "/users/"+username+"/emailaddresses/"+label
        return self.client.put(uri, data, headers=headers, params=query_params)


    def DeleteEmailAddress(self, label, username, headers=None, query_params=None):
        """
        Removes an email address
        It is method for DELETE /users/{username}/emailaddresses/{label}
        """
        uri = self.client.base_url + "/users/"+username+"/emailaddresses/"+label
        return self.client.session.delete(uri, headers=headers, params=query_params)


    def ValidateEmailAddress(self, data, label, username, headers=None, query_params=None):
        """
        Sends validation email to email address
        It is method for POST /users/{username}/emailaddresses/{label}/validate
        """
        uri = self.client.base_url + "/users/"+username+"/emailaddresses/"+label+"/validate"
        return self.client.post(uri, data, headers=headers, params=query_params)


    def DeleteFacebookAccount(self, username, headers=None, query_params=None):
        """
        Delete the associated facebook account
        It is method for DELETE /users/{username}/facebook
        """
        uri = self.client.base_url + "/users/"+username+"/facebook"
        return self.client.session.delete(uri, headers=headers, params=query_params)


    def DeleteGithubAccount(self, username, headers=None, query_params=None):
        """
        Unlink Github Account
        It is method for DELETE /users/{username}/github
        """
        uri = self.client.base_url + "/users/"+username+"/github"
        return self.client.session.delete(uri, headers=headers, params=query_params)


    def GetUserInformation(self, username, headers=None, query_params=None):
        """
        It is method for GET /users/{username}/info
        """
        uri = self.client.base_url + "/users/"+username+"/info"
        return self.client.session.get(uri, headers=headers, params=query_params)


    def UpdateUserName(self, data, username, headers=None, query_params=None):
        """
        Update the user his firstname and lastname
        It is method for PUT /users/{username}/name
        """
        uri = self.client.base_url + "/users/"+username+"/name"
        return self.client.put(uri, data, headers=headers, params=query_params)


    def GetNotifications(self, username, headers=None, query_params=None):
        """
        Get the list of notifications, these are pending invitations or approvals
        It is method for GET /users/{username}/notifications
        """
        uri = self.client.base_url + "/users/"+username+"/notifications"
        return self.client.session.get(uri, headers=headers, params=query_params)


    def GetUserOrganizations(self, username, headers=None, query_params=None):
        """
        Get the list organizations a user is owner or member of
        It is method for GET /users/{username}/organizations
        """
        uri = self.client.base_url + "/users/"+username+"/organizations"
        return self.client.session.get(uri, headers=headers, params=query_params)


    def LeaveOrganization(self, globalid, username, headers=None, query_params=None):
        """
        Removes the user from an organization
        It is method for DELETE /users/{username}/organizations/{globalid}/leave
        """
        uri = self.client.base_url + "/users/"+username+"/organizations/"+globalid+"/leave"
        return self.client.session.delete(uri, headers=headers, params=query_params)


    def users_byUsernameorganizations_byGlobalid_rolesrole_delete(self, role, globalid, username, headers=None, query_params=None):
        """
        Reject membership invitation in an organization.
        It is method for DELETE /users/{username}/organizations/{globalid}/roles/{role}
        """
        uri = self.client.base_url + "/users/"+username+"/organizations/"+globalid+"/roles/"+role
        return self.client.session.delete(uri, headers=headers, params=query_params)


    def AcceptMembership(self, data, role, globalid, username, headers=None, query_params=None):
        """
        Accept membership in organization
        It is method for POST /users/{username}/organizations/{globalid}/roles/{role}
        """
        uri = self.client.base_url + "/users/"+username+"/organizations/"+globalid+"/roles/"+role
        return self.client.post(uri, data, headers=headers, params=query_params)


    def UpdatePassword(self, data, username, headers=None, query_params=None):
        """
        Update the user his password
        It is method for PUT /users/{username}/password
        """
        uri = self.client.base_url + "/users/"+username+"/password"
        return self.client.put(uri, data, headers=headers, params=query_params)


    def GetUserPhoneNumbers(self, username, headers=None, query_params=None):
        """
        It is method for GET /users/{username}/phonenumbers
        """
        uri = self.client.base_url + "/users/"+username+"/phonenumbers"
        return self.client.session.get(uri, headers=headers, params=query_params)


    def RegisterNewUserPhonenumber(self, data, username, headers=None, query_params=None):
        """
        Register a new phonenumber
        It is method for POST /users/{username}/phonenumbers
        """
        uri = self.client.base_url + "/users/"+username+"/phonenumbers"
        return self.client.post(uri, data, headers=headers, params=query_params)


    def GetUserPhonenumberByLabel(self, label, username, headers=None, query_params=None):
        """
        It is method for GET /users/{username}/phonenumbers/{label}
        """
        uri = self.client.base_url + "/users/"+username+"/phonenumbers/"+label
        return self.client.session.get(uri, headers=headers, params=query_params)


    def DeleteUserPhonenumber(self, label, username, headers=None, query_params=None):
        """
        Removes a phonenumber
        It is method for DELETE /users/{username}/phonenumbers/{label}
        """
        uri = self.client.base_url + "/users/"+username+"/phonenumbers/"+label
        return self.client.session.delete(uri, headers=headers, params=query_params)


    def UpdateUserPhonenumber(self, data, label, username, headers=None, query_params=None):
        """
        Update the label and/or value of an existing phonenumber.
        It is method for PUT /users/{username}/phonenumbers/{label}
        """
        uri = self.client.base_url + "/users/"+username+"/phonenumbers/"+label
        return self.client.put(uri, data, headers=headers, params=query_params)


    def VerifyPhoneNumber(self, data, label, username, headers=None, query_params=None):
        """
        Verifies a phone number
        It is method for PUT /users/{username}/phonenumbers/{label}/activate
        """
        uri = self.client.base_url + "/users/"+username+"/phonenumbers/"+label+"/activate"
        return self.client.put(uri, data, headers=headers, params=query_params)


    def ValidatePhonenumber(self, data, label, username, headers=None, query_params=None):
        """
        Sends validation text to phone numbers
        It is method for POST /users/{username}/phonenumbers/{label}/activate
        """
        uri = self.client.base_url + "/users/"+username+"/phonenumbers/"+label+"/activate"
        return self.client.post(uri, data, headers=headers, params=query_params)


    def ListPublicKeys(self, username, headers=None, query_params=None):
        """
        Lists all public keys
        It is method for GET /users/{username}/publickeys
        """
        uri = self.client.base_url + "/users/"+username+"/publickeys"
        return self.client.session.get(uri, headers=headers, params=query_params)


    def AddPublicKey(self, data, username, headers=None, query_params=None):
        """
        Add a public key
        It is method for POST /users/{username}/publickeys
        """
        uri = self.client.base_url + "/users/"+username+"/publickeys"
        return self.client.post(uri, data, headers=headers, params=query_params)


    def DeletePublicKey(self, label, username, headers=None, query_params=None):
        """
        Delete a public key
        It is method for DELETE /users/{username}/publickeys/{label}
        """
        uri = self.client.base_url + "/users/"+username+"/publickeys/"+label
        return self.client.session.delete(uri, headers=headers, params=query_params)


    def UpdatePublicKey(self, data, label, username, headers=None, query_params=None):
        """
        Upates the label and/or key of an existing public key
        It is method for PUT /users/{username}/publickeys/{label}
        """
        uri = self.client.base_url + "/users/"+username+"/publickeys/"+label
        return self.client.put(uri, data, headers=headers, params=query_params)


    def GetPublicKey(self, label, username, headers=None, query_params=None):
        """
        Get a public key
        It is method for GET /users/{username}/publickeys/{label}
        """
        uri = self.client.base_url + "/users/"+username+"/publickeys/"+label
        return self.client.session.get(uri, headers=headers, params=query_params)


    def ListUserRegistry(self, username, headers=None, query_params=None):
        """
        Lists the Registry entries
        It is method for GET /users/{username}/registry
        """
        uri = self.client.base_url + "/users/"+username+"/registry"
        return self.client.session.get(uri, headers=headers, params=query_params)


    def AddUserRegistryEntry(self, data, username, headers=None, query_params=None):
        """
        Adds a RegistryEntry to the user's registry, if the key is already used, it is overwritten.
        It is method for POST /users/{username}/registry
        """
        uri = self.client.base_url + "/users/"+username+"/registry"
        return self.client.post(uri, data, headers=headers, params=query_params)


    def GetUserRegistryEntry(self, key, username, headers=None, query_params=None):
        """
        Get a RegistryEntry from the user's registry.
        It is method for GET /users/{username}/registry/{key}
        """
        uri = self.client.base_url + "/users/"+username+"/registry/"+key
        return self.client.session.get(uri, headers=headers, params=query_params)


    def DeleteUserRegistryEntry(self, key, username, headers=None, query_params=None):
        """
        Removes a RegistryEntry from the user's registry
        It is method for DELETE /users/{username}/registry/{key}
        """
        uri = self.client.base_url + "/users/"+username+"/registry/"+key
        return self.client.session.delete(uri, headers=headers, params=query_params)


    def GetTOTPSecret(self, username, headers=None, query_params=None):
        """
        It is method for GET /users/{username}/totp
        """
        uri = self.client.base_url + "/users/"+username+"/totp"
        return self.client.session.get(uri, headers=headers, params=query_params)


    def RemoveTOTP(self, username, headers=None, query_params=None):
        """
        It is method for DELETE /users/{username}/totp
        """
        uri = self.client.base_url + "/users/"+username+"/totp"
        return self.client.session.delete(uri, headers=headers, params=query_params)


    def SetupTOTP(self, data, username, headers=None, query_params=None):
        """
        It is method for POST /users/{username}/totp
        """
        uri = self.client.base_url + "/users/"+username+"/totp"
        return self.client.post(uri, data, headers=headers, params=query_params)


    def GetTwoFAMethods(self, username, headers=None, query_params=None):
        """
        Get the possible two factor authentication methods
        It is method for GET /users/{username}/twofamethods
        """
        uri = self.client.base_url + "/users/"+username+"/twofamethods"
        return self.client.session.get(uri, headers=headers, params=query_params)


    def ValidateUsername(self, username, headers=None, query_params=None):
        """
        It is method for GET /users/{username}/validate
        """
        uri = self.client.base_url + "/users/"+username+"/validate"
        return self.client.session.get(uri, headers=headers, params=query_params)
