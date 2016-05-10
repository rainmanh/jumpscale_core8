from JumpScale import j

import random
import inspect
import colored_traceback
colored_traceback.add_hook(always=True)


class AtYourServiceTester():

    def __init__(self, subname="main"):

        self.subname = subname
        self.basepath = j.sal.fs.joinPaths(j.dirs.codeDir, "github", "jumpscale", "jumpscale_ays8_testenv", subname)

        # checkout a prepared ays test repo with some special ays templates to test behaviour & easy to check outcome
        if not j.sal.fs.exists(self.basepath):
            url = "git@github.com:Jumpscale/jumpscale_ays8_testenv.git"
            repo = j.do.pullGitRepo(url)

        self._git = None

        self.aysrepo = j.atyourservice.get(subname, self.basepath)


        self.logger = j.logger.get('j.atyourservicetester')

    @property
    def git(self):
        if self._git == None:
            self._git = j.clients.git.get(self.basepath)
        return self._git

    def reset(self):
        self.aysrepo.destroy(uninstall=False)

    def gitpull(self, message="unknown"):
        self.reset()
        self.git.commit(message)
        self.git.pull()

    def gitpush(self, message="unknown"):
        self.reset()
        self.git.commit(message)
        self.git.pull()
        self.git.push()

    def doall(self):
        self.gitpull()
        self.test_init()
        self.test_install()
        self.test_change_1template_method()
        self.test_change_1template_schema()
        self.test_change_blueprint()
        self.test_change_instancehrd()

    def test_init(self):
        if self.subname != "main":
            raise j.exceptions.Input("test only supported on main")
        # test basic init
        # check that some required aysi are there (do some finds)
        # some other basic tests
        self.aysrepo.init()

        # check that everything specified in the blueprint was inited.
        for blueprint in self.aysrepo.blueprints:
            for model in blueprint.models:
                for key, _ in model.items():
                    aysrole, aysinstance = key.split('__')
                    aysrole = aysrole.split('.')[0]
                    assert len(j.sal.fs.walk(j.sal.fs.joinPaths(self.basepath, 'services'), recurse=1, pattern='%s!%s' % (aysrole, aysinstance),
                               return_folders=1, return_files=0)) == 1, '%s!%s not init-ed' % (aysrole, aysinstance)
        self.logger.info('Blueprint services all accounted for')

        # Make sure all children are subdirectories of parents
        # Make sure all producers exist
        for name, service in self.aysrepo.services.items():
            assert j.sal.fs.exists(service.path), 'service "%s" files missing' % name
            assert service.parent.path if service.parent else service.path in service.path, 'service "%s" has parent "%s" but is not a child directory' % (name, self.parent)
            for role, producers in service.producers.items():
                for producer in producers:
                    assert j.sal.fs.exists(producer.path), 'service "%s" has producer of role "%s", but seems to be missing' % (name, role)
        self.logger.info('All producers accounted for')

    def test_install(self):
        if self.subname != "main":
            raise j.exceptions.Input("test only supported on main")
        self.test_init()

        run_services = list()
        run = self.aysrepo.getRun(action='install')
        for run_step in run.steps:
            for service in run_step.services:
                state = service.state.get(run_step.action, die=False)
                if not state:
                    continue
                assert state[0] != 'ERROR', "%s state was %s" % (service, state)
                run_services.append(service)
                missing_producers = [aysi for  producers in service.producers.values() for aysi in producers if aysi not in run_services]
                assert not missing_producers, 'Producers should have already run! producer %s of service %s hasn\'t' % (missing_producers, service)
        self.logger.info('No errors in install simulation')
        self.logger.info('Producers always preceding consumers! Order is correct')

        run.execute()
        # test install
        # ask for simulation first, check that the ays will be done in right order (using the producers)
        # some other basic tests

    def test_change_1template_method(self):
        first_run = self.aysrepo.getRun(action='init')
        if self.subname != "main":
            raise j.exceptions.Input("test only supported on main")
        templates_with_action_files = [service for service in self.aysrepo.services.values() if j.sal.fs.exists(service.recipe.template.path_actions)]
        random_service = random.choice(templates_with_action_files)
        random_method = random.choice(list(random_service.action_methods.values()))
        recipe_path = j.sal.fs.joinPaths(random_service.recipe.template.path, "actions.py")
        _, linenumber = inspect.getsourcelines(random_method)
        with open(recipe_path, 'r') as file:
            data = file.read().splitlines()

        original_line = data[linenumber+1]
        data[linenumber+1] = '%s # testing changing the template' % original_line

        # and write everything back
        with open(recipe_path, 'w') as file:
            file.writelines(data)

        self.aysrepo._services = {}  # to reload everything

        second_run = self.aysrepo.getRun(action='init')

        # check second_run only contains changed 
        # change 1 template method
        # ask for aysrun for init, check the aysrun is ok, right aysi impacted
        # do init
        # check that right ays were impacted and only the ones required (through state object)

    def test_change_1template_schema(self):
        if self.subname != "main":
            raise j.exceptions.Input("test only supported on main")
        # change 1 template schema (add variable)
        # ask for aysrun for init, check the aysrun is ok, right aysi impacted
        # do init
        # check that right ays were impacted and only the ones required (through state object)
        # do now same for remove of variable

    def test_change_blueprint(self):
        if self.subname != "main":
            raise j.exceptions.Input("test only supported on main")
        # change an argument in blueprint
        # ask for aysrun for init, check the aysrun is ok, right aysi impacted
        # do init
        # check that right ays were impacted and only the ones required (through state object)
        # do now same for additional aysi in blueprint

    def test_change_instancehrd(self):
        if self.subname != "main":
            raise j.exceptions.Input("test only supported on main")
        # change hrd for 1 instance
        # ask for aysrun for init, check the aysrun is ok, right aysi impacted
        # do init
        # check that right ays were impacted and only the ones required (through state object)

        # result should be that the install action is changed
