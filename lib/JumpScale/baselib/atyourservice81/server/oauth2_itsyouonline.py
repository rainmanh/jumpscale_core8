from functools import wraps
from asyncio import get_event_loop

from sanic.response import text

from jose import jwt

oauth2_server_pub_key = """"""

token_prefix = 'Bearer '

class oauth2_itsyouonline:
    def __init__(self, scopes=None, audience= None):
        
        self.described_by = "headers"
        self.field = "Authorization"
        
        self.allowed_scopes = scopes
        if audience is None:
            self.audience = ''
        else:
            self.audience = ",".join(audience)

    def __call__(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not self.check_token(args[1]):
            	return text("", 401)
            
            return f(*args, **kwargs)
        
        return decorated_function

    async def check_token(self, request):
    	# check provided token
    	token = self.get_token(request)

    	if len(token) == 0:
    		return False

    	if not await self.check_jwt_scopes(token):
    		return False

    	return True

    async def check_jwt_scopes(self, token):
    	if len(oauth2_server_pub_key) == 0:
    		return True

    	#scopes = jwt.decode(token, oauth2_server_pub_key, audience=self.audience)["scope"]
    	scopes = (await get_event_loop().run_in_executor(None, jwt.decode, token, oauth2_server_pub_key, None, None, self.audience))['scope']
    	
    	if len(self.allowed_scopes) == 0:
    		return True

    	for allowed in self.allowed_scopes:
    		for s in scopes:
    			if s == allowed:
    				return True

    	return False

    def get_token(self, request):
    	if self.described_by == 'headers':
    		header = request.headers.get(self.field, '')
    		if header.startswith(token_prefix):
    			return header[len(token_prefix):]
    		else:
    			return ''
    	elif self.described_by == 'queryParameters':
    		return request.args.get("access_token", "")
    	else:
    		return ''