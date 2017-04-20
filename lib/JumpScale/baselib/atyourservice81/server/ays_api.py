import json as JSON
from sanic.response import json, text
import jsonschema
from jsonschema import Draft4Validator
import asyncio
import capnp

from JumpScale.baselib.atyourservice81.server.views import service_view
from JumpScale.baselib.atyourservice81.server.views import run_view
from JumpScale.baselib.atyourservice81.server.views import actor_view
from JumpScale.baselib.atyourservice81.server.views import blueprint_view
from JumpScale.baselib.atyourservice81.server.views import template_view
from JumpScale.baselib.atyourservice81.server.views import repository_view

from JumpScale import j

Blueprint_schema = JSON.load(open(j.sal.fs.joinPaths(j.sal.fs.getParent(__file__),'schema/Blueprint_schema.json')))
Repository_schema = JSON.load(open(j.sal.fs.joinPaths(j.sal.fs.getParent(__file__),'schema/Repository_schema.json')))
TemplateRepo_schema = JSON.load(open(j.sal.fs.joinPaths(j.sal.fs.getParent(__file__),'schema/TemplateRepo_schema.json')))

AYS_REPO_DIR = '/optvar/cockpit_repos'

async def reload(request):
    try:
        j.atyourservice.reset()
        return json({})
    except Exception as e:
        return json({'error': e.message}, 500)

async def addTemplateRepo(request):
    '''
    add a new actor template repository
    It is handler for POST /ays/template_repo
    '''

    inputs = request.json
    try:
        Draft4Validator(TemplateRepo_schema).validate(inputs)
    except jsonschema.ValidationError as e:
        return text('Bad Request Body', 400)

    # TODO
    return json({})

async def listRepositories(request):
    '''
    list all repositorys
    It is handler for GET /ays/repository
    '''
    if j.atyourservice.aysRepos is None:
        j.atyourservice.start()
    if not j.atyourservice.aysRepos:
        return json([])
    repos = [repository_view(repo) for repo in j.atyourservice.aysRepos.list()]
    return json(repos)

async def createRepository(request):
    '''
    create a new repository
    It is handler for POST /ays/repository
    '''
    inputs = request.json
    try:
        Draft4Validator(Repository_schema).validate(inputs)
    except jsonschema.ValidationError as e:
        return text('Bad Request Body', 400)

    try:
        repo = get_repo(inputs['name'])
        return json({'error': 'AYS Repository "%s" already exsits' % inputs['name']}, 409)
    except j.exceptions.NotFound:
        pass

    try:
        path = j.sal.fs.joinPaths(AYS_REPO_DIR, inputs['name'])
        repo = j.atyourservice.aysRepos.create(path, git_url=inputs['git_url'])
        return json(repository_view(repo), 201)
    except Exception as err:
        # clean directory if something went wrong during creation
        if j.sal.fs.exists(path):
            j.sal.fs.removeDirTree(path)
        raise err


async def getRepository(request, repository):
    '''
    Get information of a repository
    It is handler for GET /ays/repository/<repository>
    '''

    try:
        repo = get_repo(repository)
        return json(repository_view(repo), 200)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)

async def deleteRepository(request, repository):
    '''
    Delete a repository
    It is handler for DELETE /ays/repository/<repository>
    '''

    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error':e.message}, 404)

    await repo.delete()
    if j.sal.fs.exists(repo.path):
        j.sal.fs.removeDirTree(repo.path)

    return json({}, 204)

async def destroyRepository(request, repository):
    '''
    Delete a repository
    It is handler for POST /ays/repository/<repository>/destroy
    '''

    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error':e.message}, 404)

    await repo.destroy()

    return json({}, 204)


async def listTemplates(request, repository):
    '''
    list all templates
    It is handler for GET /ays/repository/<repository>/template
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)
    templates = [template_view(templ) for templ in repo.templates.values()]
    return json(templates, 200)


async def getTemplate(request, template, repository):
    '''
    Get a template
    It is handler for GET /ays/repository/<repository>/template/<template>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error':e.message}, 404)

    template_names = list(repo.templates.keys())
    if template not in template_names:
        return json({'error': 'tempalte not found'}, 404)

    tmpl = repo.templates[template]
    template = template_view(tmpl)

    return json(template, 200)


async def listAYSTemplates(request):
    '''
    list all templates in ays_jumpscale
    It is hadnler for GET /ays/templates
    '''
    if j.atyourservice.aysRepos is None:
        j.atyourservice.start()
    try:
        templates = [template_view(templ) for templ in j.atyourservice.actorTemplates]
    except j.exceptions.NotFound as e:
        return json({'error': 'No templates found'}, 404)
    return json(templates, 200)


async def getAYSTemplate(request, template):
    '''
    list all templates in ays_jumpscale
    It is hadnler for GET /ays/templates
    '''
    if j.atyourservice.aysRepos is None:
        j.atyourservice.start()
    try:
        for tmpl in j.atyourservice.actorTemplates:
            if tmpl.name == template:
                template = template_view(tmpl)
                break
    except j.exceptions.NotFound as e:
        return json({'error': 'No templates found'}, 404)
    return json(template, 200)


async def listRuns(request, repository):
    '''
    list all runs of the repository
    It is handler for GET /ays/repository/<repository>/aysrun
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error':e.message}, 404)

    runs = repo.runsList()
    runs = [{'key': run.model.key, 'epoch': run.model.dbobj.lastModDate, 'state': str(run.state)} for run in runs]

    return json(runs, 200)

async def createRun(request, repository):
    '''
    Create a run based on all the action scheduled. This call returns an AYSRun object describing what is going to hapen on the repository.
    This is an asyncronous call. To be notify of the status of the run when then execution is finised or when an error occurs, you need to specify a callback url.
    A post request will be send to this callback url with the status of the run and the key of the run. Using this key you can inspect in detail the result of the run
    using the 'GET /ays/repository/{repository}/aysrun/{aysrun_key}' endpoint
    It is handler for POST /ays/repository/<repository>/aysrun
    '''
    def cb(future):
        # TODO: request to callback_url
        exception = future.exception()
        if exception is not None:
            print("error during execution of the run")
            print(exception)

    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error':e.message}, 404)

    simulate = j.data.types.bool.fromString(request.args.get('simulate', 'False'))
    callback_url = request.args.get('callback_url', None)

    try:
        run = repo.runCreate()
        run.save()
        if not simulate:
            future = asyncio.ensure_future(run.execute())
            future.add_done_callback(cb)

        return json(run_view(run), 200)

    except j.exceptions.Input as e:
        return json({'error': e.msgpub}, 500)
    except Exception as e:
        raise e
        # return json({'error':"Unexpected error: {}".format(str(e))}, 500)

async def getRun(request, aysrun, repository):
    '''
    Get an aysrun
    It is handler for GET /ays/repository/<repository>/aysrun/<aysrun>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error':e.message}, 404)

    try:
        aysrun_model = repo.runGet(aysrun)
    except j.exceptions.NotFound as e:
        return json({'error':e.message}, 404)

    aysrun = aysrun_model.objectGet()
    return json(run_view(aysrun), 200)

async def deleteRun(request, aysrun, repository):
    '''
    Delete an aysrun
    It is handler for DELETE /ays/repository/<repository>/aysrun/<aysrun>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error':e.message}, 404)

    try:
        repo.runDelete(aysrun)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)


async def executeRun(request, aysrun, repository):
    """
    Execute a specific run
    """
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)

    try:
        aysrun_model = repo.runGet(aysrun)
        aysrun = aysrun_model.objectGet()
        await repo.run_scheduler.add(aysrun)

    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)

    except Exception as e:
        return json({'error': str(e)}, 500)

    return json(run_view(aysrun), 200)


async def listBlueprints(request, repository):
    '''
    List all blueprint
    It is handler for GET /ays/repository/<repository>/blueprint
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error':e.message}, 404)
    include_archived = j.data.types.bool.fromString(request.args.get('archived', 'True'))
    blueprints = [{'name': blueprint.name} for blueprint in repo.blueprints]

    if include_archived:
        for blueprint in repo.blueprintsDisabled:
            blueprints.append({'name': blueprint.name})
    return json(blueprints, 200)

async def createBlueprint(request, repository):
    '''
    Create a new blueprint
    It is handler for POST /ays/repository/<repository>/blueprint
    '''

    inputs = request.json
    try:
        Draft4Validator(Blueprint_schema).validate(inputs)
    except jsonschema.ValidationError as e:
        return text('Bad Request Body :%s' % e, 400)

    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error':e.message}, 404)

    new_name = inputs['name']
    content = inputs['content']
    names = [bp.name for bp in repo.blueprints]
    if new_name in names:
        return json({'error':"Blueprint with the name %s' already exists" % new_name}, 409)


    bp_path = j.sal.fs.joinPaths(repo.path, 'blueprints', new_name)
    try:
        j.sal.fs.writeFile(bp_path, content)
        blueprint = repo.blueprintGet(new_name)
    except Exception as e:
        print(str(e))
        if j.sal.fs.exists(bp_path):
            j.sal.fs.remove(bp_path)
        return json({'error':"Can't save new blueprint"}, 500)

    # check validity of input as blueprint syntax
    try:
        blueprint.validate()
    except:
        if j.sal.fs.exists(bp_path):
            j.sal.fs.remove(bp_path)
        return json({'error':"Invalid blueprint syntax"}, 500)

    return json(blueprint_view(blueprint), 201)

async def getBlueprint(request, blueprint, repository):
    '''
    Get a blueprint
    It is handler for GET /ays/repository/<repository>/blueprint/<blueprint>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error':e.message}, 404)

    bp = None
    blueprints = repo.blueprints + repo.blueprintsDisabled
    for item in blueprints:
        if blueprint == item.name:
            bp = item
            break
    else:
        return json({'error':"No blueprint found with this name '%s'" % blueprint}, 404)

    return json(blueprint_view(bp), 200)

async def executeBlueprint(request, blueprint, repository):
    '''
    Execute the blueprint
    It is handler for POST /ays/repository/<repository>/blueprint/<blueprint>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error':e.message}, 404)

    bp = None
    blueprints = repo.blueprints + repo.blueprintsDisabled
    for item in blueprints:
        if item.name == blueprint:
            bp = item
            break
    else:
        return json({'error':"No blueprint found with this name '{}'".format(blueprint)}, 404)

    try:
        await repo.blueprintExecute(path=bp.path)
    except Exception as e:
        error_msg = "Error during execution of the blueprint:\n %s" % str(e)
        j.atyourservice.logger.exception(error_msg)
        return json({'error': error_msg}, 500)

    return json({'msg':'Blueprint {} executed'.format(blueprint)})

async def updateBlueprint(request, blueprint, repository):
    '''
    Update existing blueprint
    It is handler for PUT /ays/repository/<repository>/blueprint/<blueprint>
    '''

    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error':e.message}, 404)

    inputs = request.json
    try:
        Draft4Validator(Blueprint_schema).validate(inputs)
    except jsonschema.ValidationError as e:
        return text('Bad Request Body', 400)


    name = inputs['name']

    names = [bp.name for bp in repo.blueprints]
    names.extend([bp.name for bp in repo.blueprintsDisabled])
    if name not in names:
        return json({'error':"blueprint with the name %s not found" % name}, 404)

    blueprint_path = j.sal.fs.joinPaths(repo.path, 'blueprints', name)
    blueprint = repo.blueprintGet(blueprint_path)
    content = j.data.serializer.yaml.dumps(inputs['content'])
    blueprint.content = content
    j.sal.fs.writeFile(blueprint_path, content)

    return json(blueprint_view(blueprint), 200)

async def deleteBlueprint(request, blueprint, repository):
    '''
    delete blueprint
    It is handler for DELETE /ays/repository/<repository>/blueprint/<blueprint>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error':e.message}, 404)

    by_names = {bp.name: bp for bp in repo.blueprints}
    for bp in repo.blueprintsDisabled:
        by_names[bp.name] = bp

    if blueprint not in by_names:
        return json({'error': "blueprint with the name %s not found" % blueprint}, 404)

    bp = by_names[blueprint]

    if j.sal.fs.exists(bp.path):
        j.sal.fs.remove(bp.path)

    return json({}, 204)

async def archiveBlueprint(request, blueprint, repository):
    '''
    archive the blueprint
    It is handler for PUT /ays/repository/<repository>/blueprint/<blueprint>/archive
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error':e.message}, 404)

    by_names = {bp.name: bp for bp in repo.blueprints}
    if blueprint not in by_names:
        return json({'error':"blueprint with the name %s not found" % blueprint}, 404)

    by_names[blueprint].disable()

    return json({'msg':'Blueprint %s archived' % blueprint}, 200)

async def restoreBlueprint(request, blueprint, repository):
    '''
    restore the blueprint
    It is handler for PUT /ays/repository/<repository>/blueprint/<blueprint>/restore
    '''

    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error':e.message}, 404)

    by_names = {bp.name: bp for bp in repo.blueprintsDisabled}
    if blueprint not in by_names:
        return json({'error':"blueprint with the name %s not found" % blueprint}, 404)

    by_names[blueprint].enable()

    return json({'msg':'Blueprint %s restored' % blueprint}, 200)

async def listServices(request, repository):
    '''
    List all services in the repository
    It is handler for GET /ays/repository/<repository>/service
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error':e.message}, 404)

    services = list()
    for s in repo.services:
         services.append({'role': s.model.role, 'name': s.name})
    services = sorted(services, key=lambda service: service['role'])

    return json(services, 200)

def _sanitize(value):
    if isinstance(value, (list, capnp.lib.capnp._DynamicListBuilder)):
        result = list()
        for item in value:
            result.append(_sanitize(item))
        return result
    elif isinstance(value, (dict, capnp.lib.capnp._DynamicStructBuilder)):
        result = dict()
        for key, val in value.to_dict().items():
            result[key] = _sanitize(val)
        return result
    elif isinstance(value, capnp.lib.capnp._DynamicEnum):
        return str(value)
    else:
        return value

async def listServicesByRole(request, role, repository):
    '''
    List all services of role 'role' in the repository
    It is handler for GET /ays/repository/<repository>/service/<role>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error':e.message}, 404)

    parent = request.args.get('parent', '')
    fields = request.args.get('fields', '')

    fields = [field.strip() for field in fields.split(',') if field.strip()]
    result = list()

    for s in repo.servicesFind(role=role, parent=parent):
        data = {'role': s.model.role, 'name': s.model.name, 'data':dict()}
        for field in fields:
            if not hasattr(s.model.data, field):
                return json('No such field "{}" in service "{}" data'.format(field, s), 400)
            data['data'][field] = _sanitize(getattr(s.model.data, field))
        result.append(data)
    result = sorted(result, key=lambda service: service['role'])
    return json(result, 200)

async def getServiceByName(request, name, role, repository):
    '''
    Get a service name
    It is handler for GET /ays/repository/<repository>/service/<role>/<name>
    '''

    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error':e.message}, 404)

    s = repo.serviceGet(role=role, instance=name, die=False)
    if s is None:
        return json({'error':'Service not found'}, 404)

    return json(service_view(s), 200)


async def deleteServiceByName(request, name, role, repository):
    '''
    delete a service and all its children
    It is handler for DELETE /ays/repository/<repository>/service/<role>/<name>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error':e.message}, 404)


    service = repo.serviceGet(role=role, instance=name, die=False)
    if service is None:
        return json({'error':'Service role:%s name:%s not found in the repo %s' % (role, name, repository)}, 404)

    await service.delete()

    return json({}, 204)


async def listActors(request, repository):
    '''
    list all actors in the repository
    It is handler for GET /ays/repository/<repository>/actor
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error':e.message}, 404)

    actors = [{'name': actor.model.name} for actor in repo.actors.values()]

    return json(actors, 200)


async def getActorByName(request, name, repository):
    '''
    Get an actor by name
    It is handler for GET /ays/repository/<repository>/actor/<name>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error':e.message}, 404)

    try:
        actor = repo.actorGet(name=name)
    except j.exceptions.NotFound as e:
        json({'error':'actor {} not found'.format(name)}, 404)

    return json(actor_view(actor), 200)


async def updateActor(request, name, repository):
    '''
    update an actor from a template to the last version
    It is handler for PUT /ays/repository/<repository>/actor/<name>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error':e.message}, 404)

    template = repo.templateGet(name=name)
    try:
        actor = repo.actorGet(name=name)
    except:
        return json({'error':'actor {} not found'.format(name)}, 404)

    actor._initFromTemplate(template)

    return json(actor_view(actor), 200)


def get_repo(name):
    """
    try to get a repo by his name.
    name is prepend with AYS_REPO_DIR to create the full path to the repo
    raise j.exceptions.NotFound if repo doesn't exists
    """
    if j.atyourservice.aysRepos is None:
        j.atyourservice.start()
    for repo in j.atyourservice.aysRepos.list():
        if name == repo.name:
            return repo

    raise j.exceptions.NotFound("Repository {} doesn't exists".format(name))
