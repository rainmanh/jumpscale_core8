from sanic import Blueprint
from sanic.views import HTTPMethodView
from sanic.response import text
import JumpScale.baselib.atyourservice81.server.ays_api as ays_api



ays_if = Blueprint('ays_if')


class ays_repositoryView(HTTPMethodView):

    async def get(self, request):

        return await ays_api.listRepositories(request)

    async def post(self, request):

        return await ays_api.createRepository(request)

ays_if.add_route(ays_repositoryView.as_view(), '/ays/repository')

class ays_repository_byrepositoryView(HTTPMethodView):

    async def get(self, request, repository):

        return await ays_api.getRepository(request, repository)

    async def delete(self, request, repository):

        return await ays_api.deleteRepository(request, repository)

ays_if.add_route(ays_repository_byrepositoryView.as_view(), '/ays/repository/<repository>')

class ays_repository_byrepository_actorView(HTTPMethodView):

    async def get(self, request, repository):

        return await ays_api.listActors(request, repository)

ays_if.add_route(ays_repository_byrepository_actorView.as_view(), '/ays/repository/<repository>/actor')

class ays_repository_byrepository_actor_bynameView(HTTPMethodView):

    async def get(self, request, name, repository):

        return await ays_api.getActorByName(request, name, repository)

    async def put(self, request, name, repository):

        return await ays_api.updateActor(request, name, repository)

ays_if.add_route(ays_repository_byrepository_actor_bynameView.as_view(), '/ays/repository/<repository>/actor/<name>')

class ays_repository_byrepository_aysrunView(HTTPMethodView):

    async def get(self, request, repository):

        return await ays_api.listRuns(request, repository)

    async def post(self, request, repository):

        return await ays_api.CreateRun(request, repository)

ays_if.add_route(ays_repository_byrepository_aysrunView.as_view(), '/ays/repository/<repository>/aysrun')

class ays_repository_byrepository_aysrun_byaysrunView(HTTPMethodView):

    async def get(self, request, aysrun, repository):

        return await ays_api.getRun(request, aysrun, repository)

    async def post(self, request, aysrun, repository):

        return await ays_api.executeRun(request, aysrun, repository)

ays_if.add_route(ays_repository_byrepository_aysrun_byaysrunView.as_view(), '/ays/repository/<repository>/aysrun/<aysrun>')

class ays_repository_byrepository_blueprintView(HTTPMethodView):

    async def get(self, request, repository):

        return await ays_api.listBlueprints(request, repository)

    async def post(self, request, repository):

        return await ays_api.createBlueprint(request, repository)

ays_if.add_route(ays_repository_byrepository_blueprintView.as_view(), '/ays/repository/<repository>/blueprint')

class ays_repository_byrepository_blueprint_byblueprintView(HTTPMethodView):

    async def get(self, request, blueprint, repository):

        return await ays_api.getBlueprint(request, blueprint, repository)

    async def post(self, request, blueprint, repository):

        return await ays_api.executeBlueprint(request, blueprint, repository)

    async def put(self, request, blueprint, repository):

        return await ays_api.updateBlueprint(request, blueprint, repository)

    async def delete(self, request, blueprint, repository):

        return await ays_api.deleteBlueprint(request, blueprint, repository)

ays_if.add_route(ays_repository_byrepository_blueprint_byblueprintView.as_view(), '/ays/repository/<repository>/blueprint/<blueprint>')

class ays_repository_byrepository_blueprint_byblueprint_archiveView(HTTPMethodView):

    async def put(self, request, blueprint, repository):

        return await ays_api.archiveBlueprint(request, blueprint, repository)

ays_if.add_route(ays_repository_byrepository_blueprint_byblueprint_archiveView.as_view(), '/ays/repository/<repository>/blueprint/<blueprint>/archive')

class ays_repository_byrepository_blueprint_byblueprint_restoreView(HTTPMethodView):

    async def put(self, request, blueprint, repository):

        return await ays_api.restoreBlueprint(request, blueprint, repository)

ays_if.add_route(ays_repository_byrepository_blueprint_byblueprint_restoreView.as_view(), '/ays/repository/<repository>/blueprint/<blueprint>/restore')

class ays_repository_byrepository_serviceView(HTTPMethodView):

    async def get(self, request, repository):

        return await ays_api.listServices(request, repository)

ays_if.add_route(ays_repository_byrepository_serviceView.as_view(), '/ays/repository/<repository>/service')

class ays_repository_byrepository_service_byroleView(HTTPMethodView):

    async def get(self, request, role, repository):

        return await ays_api.listServicesByRole(request, role, repository)

ays_if.add_route(ays_repository_byrepository_service_byroleView.as_view(), '/ays/repository/<repository>/service/<role>')

class ays_repository_byrepository_service_byrole_bynameView(HTTPMethodView):

    async def get(self, request, name, role, repository):

        return await ays_api.getServiceByName(request, name, role, repository)

    async def delete(self, request, name, role, repository):

        return await ays_api.deleteServiceByName(request, name, role, repository)

ays_if.add_route(ays_repository_byrepository_service_byrole_bynameView.as_view(), '/ays/repository/<repository>/service/<role>/<name>')

class ays_repository_byrepository_templateView(HTTPMethodView):

    async def get(self, request, repository):

        return await ays_api.listTemplates(request, repository)

ays_if.add_route(ays_repository_byrepository_templateView.as_view(), '/ays/repository/<repository>/template')

class ays_repository_byrepository_template_bytemplateView(HTTPMethodView):

    async def get(self, request, template, repository):

        return await ays_api.getTemplate(request, template, repository)

ays_if.add_route(ays_repository_byrepository_template_bytemplateView.as_view(), '/ays/repository/<repository>/template/<template>')

class ays_template_repoView(HTTPMethodView):

    async def post(self, request):

        return await ays_api.addTemplateRepo(request)

ays_if.add_route(ays_template_repoView.as_view(), '/ays/template_repo')
