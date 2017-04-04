import urllib.request
import urllib.parse
import urllib.error
import string
import requests
import time
import random


from JumpScale import j


class AuthError(Exception):
    pass


class UserInfo(object):

    def __init__(self, username, emailaddress, groups):
        self.username = username
        self.emailaddress = emailaddress
        self.groups = groups


class OauthInstance:

    def __init__(self, addr, accesstokenaddr, id, secret, scope, redirect_url, user_info_url, logout_url, instance):
        if not addr:
            hrd = j.application.getAppInstanceHRD('oauth_client', instance)
            self.addr = hrd.get('instance.oauth.client.url')
            self.accesstokenaddress = hrd.get('instance.oauth.client.url2')
            self.id = hrd.get('instance.oauth.client.id')
            self.scope = hrd.get('instance.oauth.client.scope')
            self.redirect_url = hrd.get('instance.oauth.client.redirect_url')
            self.secret = hrd.get('instance.oauth.client.secret')
            self.user_info_url = hrd.get('instance.oauth.client.user_info_url')
            self.logout_url = hrd.get('instance.oauth.client.logout_url')
        else:
            self.addr = addr
            self.id = id
            self.scope = scope
            self.redirect_url = redirect_url
            self.accesstokenaddress = accesstokenaddr
            self.secret = secret
            self.user_info_url = user_info_url
            self.logout_url = logout_url
        self.state = ''.join(random.choice(
            string.ascii_uppercase + string.digits) for _ in range(30))

    @property
    def url(self):
        params = {'client_id': self.id, 'redirect_uri': self.redirect_url,
                  'state': self.state, 'response_type': 'code'}
        if self.scope:
            params.update({'scope': self.scope})
        return '%s?%s' % (self.addr, urllib.parse.urlencode(params))

    def getAccessToken(self, code, state):
        payload = {'code': code, 'client_id': self.id, 'client_secret': self.secret,
                   'redirect_uri': self.redirect_url, 'grant_type': 'authorization_code',
                   'state': state}
        result = requests.post(self.accesstokenaddress, data=payload, headers={
            'Accept': 'application/json'})

        if not result.ok or 'error' in result.json():
            msg = result.json()['error']
            j.logger.log(msg)
            raise AuthError(msg)
        return result.json()

    def getUserInfo(self, accesstoken):
        params = {'access_token': accesstoken['access_token']}
        userinforesp = requests.get(self.user_info_url, params=params)
        if not userinforesp.ok:
            msg = 'Failed to get user details'
            j.logger.log(msg)
            raise AuthError(msg)

        userinfo = userinforesp.json()
        return UserInfo(userinfo['login'], userinfo['email'], ['user'])


class ItsYouOnline(OauthInstance):

    def getAccessToken(self, code, state):
        import jose
        import jose.jwt
        scope = self.scope + ',offline_access'
        organization = j.portal.server.active.cfg['oauth.organization']
        payload = {'code': code, 'client_id': self.id, 'client_secret': self.secret,
                   'redirect_uri': self.redirect_url, 'grant_type': '', 'scope': scope,
                   'response_type': 'id_token', 'state': state, 'aud': organization}
        result = requests.post(self.accesstokenaddress, data=payload, headers={
            'Accept': 'application/json'})

        if not result.ok:
            msg = result.text
            j.logger.log(msg)
            raise AuthError(msg)
        token = result.json()
        # convert jwt expire time to oauth2 token expire time
        jwtdata = jose.jwt.get_unverified_claims(token['access_token'])
        token['expires_in'] = jwtdata['exp'] - time.time()
        return token

    def getUserInfo(self, accesstoken):
        import jose
        import jose.jwt
        jwt = accesstoken['access_token']
        headers = {'Authorization': 'bearer %s' % jwt}

        jwtdata = jose.jwt.get_unverified_claims(jwt)
        scopes = jwtdata['scope']
        requestedscopes = set(self.scope.split(','))
        if set(jwtdata['scope']).intersection(requestedscopes) != requestedscopes:
            msg = 'Failed to get the requested scope for %s' % self.client.id
            raise AuthError(msg)

        username = jwtdata['username']
        userinfourl = self.user_info_url.rstrip('/') + "/%s/info" % username
        userinforesp = requests.get(userinfourl, headers=headers)
        if not userinforesp.ok:
            msg = 'Failed to get user details'
            raise AuthError(msg)

        groups = ['user']
        for scope in scopes:
            parts = scope.split(':')
            if len(parts) == 3 and parts[:2] == ['user', 'memberof']:
                groups.append(parts[-1].split('.')[-1])

        userinfo = userinforesp.json()
        return UserInfo(userinfo['username'], userinfo['emailaddresses'][0]['emailaddress'], groups)
