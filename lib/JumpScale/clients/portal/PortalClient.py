import requests
import os
import json


class ApiError(Exception):

    def __init__(self, response):
        msg = '%s %s' % (response.status_code, response.reason)
        try:
            message = response.json()
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


class BaseResource:

    def __init__(self, session, url):
        self._session = session
        self._url = url

    def __getattr__(self, item):
        url = os.path.join(self._url, item)
        resource = BaseResource(self._session, url)
        setattr(self, item, resource)
        return resource

    def __call__(self, **kwargs):
        response = self._session.post(self._url, kwargs)

        if not response.ok:
            raise ApiError(response)

        if response.headers.get('content-type', 'text/html') == 'application/json':
            return response.json()

        return response.content


class Resource(BaseResource):

    def __init__(self, ip, port, secret, path):
        session = requests.Session()

        if secret is not None:
            session.cookies['beaker.session.id'] = secret

        scheme = "http" if port != 443 else "https"
        url = "%s://%s:%s/%s" % (scheme, ip, port, path.lstrip('/'))

        super(Resource, self).__init__(session, url)

    def load_swagger(self, file=None, group=None):
        if file:
            with open(file) as fd:
                swagger = json.load(fd)
        else:
            swagger = self.system.docgenerator.prepareCatalog(group=group)

        for methodpath, methodspec in swagger['paths'].items():
            api = self
            for path in methodpath.split('/')[1:]:
                api = getattr(api, path)
            if 'post' not in methodspec:
                continue
            docstring = methodspec['post']['description']
            for param in methodspec['post'].get('parameters', list()):
                param['type'] = param['type'] if 'type' in param else str(
                    param.get('$ref', 'unknown'))
                docstring += """
                :param %(name)s: %(description)s required %(required)s
                :type %(name)s: %(type)s""" % param
            api.__doc__ = docstring
        return swagger
