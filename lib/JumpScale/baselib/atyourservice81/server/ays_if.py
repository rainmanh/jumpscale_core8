from sanic import Blueprint
from sanic.views import HTTPMethodView
from sanic.response import text
import JumpScale.baselib.atyourservice81.server.ays_api as ays_api

from JumpScale.baselib.atyourservice81.server.oauth2_itsyouonline import oauth2_itsyouonline

ays_if = Blueprint('ays_if')

class ays_repositoryView(HTTPMethodView):

    async def get(self, request):

        code, msg = await oauth2_itsyouonline(["user:memberof:organization"]).check_token(request)
        if code != 200:
            return text(msg, code)
        return await ays_api.listRepositories(request)

    async def post(self, request):
        msg, code = await oauth2_itsyouonline(["user:memberof:organization"]).check_token(request)
        if code != 200:
            return text(msg, code)

        return await ays_api.createRepository(request)

ays_if.add_route(ays_repositoryView.as_view(), '/ays/repository')

class ays_repository_byrepository_nameView(HTTPMethodView):

    async def get(self, request, repository_name):

        msg, code = await oauth2_itsyouonline(["user:memberof:organization"]).check_token(request)
        if code != 200:
            return text(msg, code)
            

        return await ays_api.getRepository(request, repository_name)

    async def delete(self, request, repository_name):

        msg, code = await oauth2_itsyouonline(["user:memberof:organization"]).check_token(request)
        if code != 200:
            return text(msg, code)

        return await ays_api.deleteRepository(request, repository_name)

ays_if.add_route(ays_repository_byrepository_nameView.as_view(), '/ays/repository/<repository_name>')

class ays_repository_byrepository_name_actorView(HTTPMethodView):

    async def get(self, request, repository_name):

        msg, code = await oauth2_itsyouonline(["user:memberof:organization"]).check_token(request)
        if code != 200:
            return text(msg, code)

        return await ays_api.listActors(request, repository_name)

ays_if.add_route(ays_repository_byrepository_name_actorView.as_view(), '/ays/repository/<repository_name>/actor')

class ays_repository_byrepository_name_actor_byactor_nameView(HTTPMethodView):

    async def get(self, request, actor_name, repository_name):

        msg, code = await oauth2_itsyouonline(["user:memberof:organization"]).check_token(request)
        if code != 200:
            return text(msg, code)

        return await ays_api.getActorByName(request, actor_name, repository_name)

    async def put(self, request, actor_name, repository_name):

        msg, code = await oauth2_itsyouonline(["user:memberof:organization"]).check_token(request)
        if code != 200:
            return text(msg, code)

        return await ays_api.updateActor(request, actor_name, repository_name)

ays_if.add_route(ays_repository_byrepository_name_actor_byactor_nameView.as_view(), '/ays/repository/<repository_name>/actor/<actor_name>')

class ays_repository_byrepository_name_aysrunView(HTTPMethodView):

    async def get(self, request, repository_name):

        msg, code = await oauth2_itsyouonline(["user:memberof:organization"]).check_token(request)
        if code != 200:
            return text(msg, code)

        return await ays_api.listRuns(request, repository_name)

    async def post(self, request, repository_name):

        msg, code = await oauth2_itsyouonline(["user:memberof:organization"]).check_token(request)
        if code != 200:
            return text(msg, code)

        return await ays_api.CreateRun(request, repository_name)

ays_if.add_route(ays_repository_byrepository_name_aysrunView.as_view(), '/ays/repository/<repository_name>/aysrun')

class ays_repository_byrepository_name_aysrun_byrunidView(HTTPMethodView):

    async def get(self, request, runid, repository_name):

        msg, code = await oauth2_itsyouonline(["user:memberof:organization"]).check_token(request)
        if code != 200:
            return text(msg, code)

        return await ays_api.getRun(request, runid, repository_name)

ays_if.add_route(ays_repository_byrepository_name_aysrun_byrunidView.as_view(), '/ays/repository/<repository_name>/aysrun/<runid>')

class ays_repository_byrepository_name_blueprintView(HTTPMethodView):

    async def get(self, request, repository_name):

        msg, code = await oauth2_itsyouonline(["user:memberof:organization"]).check_token(request)
        import ipdb; ipdb.set_trace()
        if code != 200:
            return text(msg, code)

        return await ays_api.listBlueprints(request, repository_name)

    async def post(self, request, repository_name):

        msg, code = await oauth2_itsyouonline(["user:memberof:organization"]).check_token(request)
        if code != 200:
            return text(msg, code)

        return await ays_api.createBlueprint(request, repository_name)

ays_if.add_route(ays_repository_byrepository_name_blueprintView.as_view(), '/ays/repository/<repository_name>/blueprint')

class ays_repository_byrepository_name_blueprint_byblueprint_nameView(HTTPMethodView):

    async def get(self, request, blueprint_name, repository_name):

        msg, code = await oauth2_itsyouonline(["user:memberof:organization"]).check_token(request)
        if code != 200:
            return text(msg, code)

        return await ays_api.getBlueprint(request, blueprint_name, repository_name)

    async def post(self, request, blueprint_name, repository_name):

        msg, code = await oauth2_itsyouonline(["user:memberof:organization"]).check_token(request)
        if code != 200:
            return text(msg, code)

        return await ays_api.executeBlueprint(request, blueprint_name, repository_name)

    async def put(self, request, blueprint_name, repository_name):

        msg, code = await oauth2_itsyouonline(["user:memberof:organization"]).check_token(request)
        if code != 200:
            return text(msg, code)

        return await ays_api.updateBlueprint(request, blueprint_name, repository_name)

    async def delete(self, request, blueprint_name, repository_name):

        msg, code = await oauth2_itsyouonline(["user:memberof:organization"]).check_token(request)
        if code != 200:
            return text(msg, code)

        return await ays_api.deleteBlueprint(request, blueprint_name, repository_name)

ays_if.add_route(ays_repository_byrepository_name_blueprint_byblueprint_nameView.as_view(), '/ays/repository/<repository_name>/blueprint/<blueprint_name>')

class ays_repository_byrepository_name_blueprint_byblueprint_name_archiveView(HTTPMethodView):

    async def put(self, request, blueprint_name, repository_name):

        msg, code = await oauth2_itsyouonline(["user:memberof:organization"]).check_token(request)
        if code != 200:
            return text(msg, code)

        return await ays_api.archiveBlueprint(request, blueprint_name, repository_name)

ays_if.add_route(ays_repository_byrepository_name_blueprint_byblueprint_name_archiveView.as_view(), '/ays/repository/<repository_name>/blueprint/<blueprint_name>/archive')

class ays_repository_byrepository_name_blueprint_byblueprint_name_restoreView(HTTPMethodView):

    async def put(self, request, blueprint_name, repository_name):

        msg, code = await oauth2_itsyouonline(["user:memberof:organization"]).check_token(request)
        if code != 200:
            return text(msg, code)

        return await ays_api.restoreBlueprint(request, blueprint_name, repository_name)

ays_if.add_route(ays_repository_byrepository_name_blueprint_byblueprint_name_restoreView.as_view(), '/ays/repository/<repository_name>/blueprint/<blueprint_name>/restore')

class ays_repository_byrepository_name_serviceView(HTTPMethodView):

    async def get(self, request, repository_name):

        msg, code = await oauth2_itsyouonline(["user:memberof:organization"]).check_token(request)
        if code != 200:
            return text(msg, code)

        return await ays_api.listServices(request, repository_name)

ays_if.add_route(ays_repository_byrepository_name_serviceView.as_view(), '/ays/repository/<repository_name>/service')

class ays_repository_byrepository_name_service_byservice_roleView(HTTPMethodView):

    async def get(self, request, service_role, repository_name):

        msg, code = await oauth2_itsyouonline(["user:memberof:organization"]).check_token(request)
        if code != 200:
            return text(msg, code)

        return await ays_api.listServicesByRole(request, service_role, repository_name)

ays_if.add_route(ays_repository_byrepository_name_service_byservice_roleView.as_view(), '/ays/repository/<repository_name>/service/<service_role>')

class ays_repository_byrepository_name_service_byservice_role_byservice_nameView(HTTPMethodView):

    async def get(self, request, service_name, service_role, repository_name):

        msg, code = await oauth2_itsyouonline(["user:memberof:organization"]).check_token(request)
        if code != 200:
            return text(msg, code)

        return await ays_api.getServiceByName(request, service_name, service_role, repository_name)

    async def delete(self, request, service_name, service_role, repository_name):

        msg, code = await oauth2_itsyouonline(["user:memberof:organization"]).check_token(request)
        if code != 200:
            return text(msg, code)

        return await ays_api.deleteServiceByName(request, service_name, service_role, repository_name)

ays_if.add_route(ays_repository_byrepository_name_service_byservice_role_byservice_nameView.as_view(), '/ays/repository/<repository_name>/service/<service_role>/<service_name>')

class ays_repository_byrepository_name_templateView(HTTPMethodView):

    async def get(self, request, repository_name):

        msg, code = await oauth2_itsyouonline(["user:memberof:organization"]).check_token(request)
        if code != 200:
            return text(msg, code)

        return await ays_api.listTemplates(request, repository_name)

ays_if.add_route(ays_repository_byrepository_name_templateView.as_view(), '/ays/repository/<repository_name>/template')

class ays_repository_byrepository_name_template_bytemplate_nameView(HTTPMethodView):

    async def get(self, request, template_name, repository_name):

        msg, code = await oauth2_itsyouonline(["user:memberof:organization"]).check_token(request)
        if code != 200:
            return text(msg, code)

        return await ays_api.getTemplate(request, template_name, repository_name)

ays_if.add_route(ays_repository_byrepository_name_template_bytemplate_nameView.as_view(), '/ays/repository/<repository_name>/template/<template_name>')

class ays_template_repoView(HTTPMethodView):

    async def post(self, request):

        msg, code = await oauth2_itsyouonline(["user:memberof:organization"]).check_token(request)
        if code != 200:
            return text(msg, code)

        return await ays_api.addTemplateRepo(request)

ays_if.add_route(ays_template_repoView.as_view(), '/ays/template_repo')
