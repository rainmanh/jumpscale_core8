import json as JSON

from sanic.response import json, text
import jsonschema
from jsonschema import Draft4Validator
from JumpScale import j

import os
dir_path = os.path.dirname(os.path.realpath(__file__))


async def webhooks_github_post(request):
    '''
    Endpoint that receives the events from github
    It is handler for POST /webhooks/github
    '''
    if request.headers.get('Content-Type') != 'application/json':
        return json({'error': 'wront content type'}, 400)

    event = request.headers.get('X-GitHub-Event')
    payload = request.json
    for repo in j.atyourservice.aysRepos.list():
        for service in repo.services:
            await service.processEvent(
                channel='webservice',
                command=event,
                secret=None,
                tags={},
                payload=payload
            )

    return json({"event executed"}, 200)
