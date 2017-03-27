from JumpScale import j

from sanic import Sanic
from sanic.response import json

from JumpScale.baselib.atyourservice81.server.ays_if import ays_if
from JumpScale.baselib.atyourservice81.server.webhooks_if import webhooks_if

from jose import jwt, exceptions

app = Sanic(__name__)
app.blueprint(ays_if)
app.blueprint(webhooks_if)

app.static('/apidocs', 'apidocs')
app.static('/', 'index.html')


cfg = j.application.config.ays['ays']

@app.middleware('request')
async def process_jwt_token(request):
    if not cfg.get('production', True):
        return
    authorization = request.cookies.get(
        'jwt',
        request.headers.get(
            'Authorization',
            None
        ))

    if authorization is None:
        return json({'error': 'No JWT token'}, 401)

    msg = ""
    ss = authorization.split(' ', 1)
    if len(ss) != 2:
        msg = "Unauthorized"
    else:
        type, token = ss[0], ss[1]
        if type.lower() == 'bearer':
            try:
                headers = jwt.get_unverified_header(token)
                payload = jwt.decode(
                    token,
                    cfg['oauth'].get('jwt_key'),
                    algorithms=[headers['alg']],
                    audience=cfg['oauth']['organization'],
                    issuer='itsyouonline')
                # case JWT is for an organization
                if 'globalid' in payload and payload['globalid'] == cfg['oauth'].get('organization'):
                    return

                # case JWT is for a user
                if 'scope' in payload and 'user:memberof:%s' % cfg[
                        'oauth'].get('organization') in payload['scope']:
                    return

                msg = 'Unauthorized'
            except exceptions.ExpiredSignatureError as e:
                msg = 'Your JWT has expired'

            except exceptions.JOSEError as e:
                msg = 'JWT Error: %s' % str(e)

            except Exception as e:
                msg = 'Unexpected error : %s' % str(e)

        else:
            msg = 'Your JWT is invalid'

    j.atyourservice.logger.error(msg)
    return json(msg, 401)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000, workers=1)
