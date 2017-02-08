from JumpScale import j
import os

def service_view(s):
    """
    generate a dict that represent a service from a service object
    """
    producers = [{'role': v.role, 'name':v.name} for v in s.model.producers]
    children = [{'role': c.model.role, 'name':c.model.name}  for c in s.children]
    service = {
        'key': s.model.key,
        'role': s.model.role,
        'name': s.name,
        'data': j.data.serializer.json.loads(s.model.dataJSON),
        'recurring': [],
        'events': [],
        'producers': producers,
        'parent': {'role': s.parent.model.role, 'name':s.parent.model.name} if s.parent else None,
        'children': children,
        'path': s.path,
        'repository': s.aysrepo.name,
        'state': s.model.dbobj.state.__str__(),
        'actions': s.model.actionsCode,
        'actions_state': [],
        'model': s.model.__repr__()
    }
    for name, model in s.model.actionsRecurring.items():
        service['recurring'].append({
            'name': name,
            'period': model.period,
            'last_run': model.lastRun
        })

    for event_filter in s.model.eventFilters:
        service['events'].append({
            'actions': event_filter.actions,
            'command': event_filter.command,
            'channel': event_filter.channel,
            'tags': event_filter.tags.split(',')
        })

    actionsNames = sorted(s.model.actionsState.keys())
    for actionName in actionsNames:
        service['actions_state'].append({
            'name':actionName,
            'state':s.model.actionsState[actionName]
        })

    return service


def run_view(run):
    """
    generate a dict that represent a run
    """
    obj = {
        'key': run.key,
        'state': str(run.state),
        'steps': [],
        'epoch': run.model.lastModDate,
    }
    for step in run.steps:
        aystep = {
            'number': step.dbobj.number,
            'jobs': [],
            'state': step.state
        }
        for job in step.jobs:
            logs = []
            for log in job.model.dbobj.logs:
                log_dict = {}
                log_record = log.to_dict()
                log_dict['epoch'] = log_record['epoch'] if 'epoch' in log_record else None
                log_dict['log'] = log_record['log'] if 'log' in log_record else None
                log_dict['level'] = log_record['level'] if 'level' in log_record else None
                log_dict['category'] = log_record['category'] if 'category' in log_record else None
                log_dict['tags'] = log_record['tags'] if 'tags' in log_record else None
                logs.append(log_dict)

            aystep['jobs'].append({
                'key': job.model.key,
                'action_name': job.model.dbobj.actionName,
                'actor_name': job.model.dbobj.actorName,
                'service_key': job.model.dbobj.serviceKey,
                'service_name': job.model.dbobj.serviceName,
                'state': str(job.model.dbobj.state),
                'logs': logs
            })
        obj['steps'].append(aystep)

    return obj


def actor_view(t):
    """
    generate a dict that represent a service from a service object
    """
    template = {
        'name': t.model.name,
        'schema_hrd': j.sal.fs.fileGetContents("{path}/schema.hrd".format(path=t.path)) if j.sal.fs.exists("{path}/schema.hrd".format(path=t.path)) else None,
        'actions_py': j.sal.fs.fileGetContents("{path}/actions.py".format(path=t.path)) if j.sal.fs.exists("{path}/actions.py".format(path=t.path)) else None,
    }
    return template


def blueprint_view(bp):
    return {
        'path': bp.path,
        'name': bp.name,
        'content': j.data.serializer.yaml.loads(bp.content),
        'hash': bp.hash,
        'archived': not bp.active,
    }

def template_view(template):
    actions_path = j.sal.fs.joinPaths(template.path, 'actions.py')
    actions_file = None
    if j.sal.fs.exists(actions_path):
        actions_file = j.sal.fs.fileGetContents(actions_path)

    return {
        'name': template.name,
        'action': actions_file or '',
        'schema': template.schemaCapnpText,
        'config': template.configDict,
    }

def repository_view(repo):
    try:
        git_url = repo.git.remoteUrl
    except:
        git_url = 'not defined'

    return {
        'name': repo.name,
        'path': repo.path,
        'git_url': git_url
    }
