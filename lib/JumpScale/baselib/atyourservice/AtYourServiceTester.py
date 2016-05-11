from JumpScale import j

import random
import inspect
import imp
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
        if self.subname != "main":
            raise j.exceptions.Input("test only supported on main")
        self.aysrepo.init()
        random_blueprint = random.choice(self.aysrepo.blueprints)
        blueprint_templates = [key.split('__')[0] for model in random_blueprint.models for key in model]

        templates_with_action_files = [self.aysrepo.getTemplate(template).path_actions for template in blueprint_templates if j.sal.fs.exists(self.aysrepo.getTemplate(template).path_actions)]
        template_path = random.choice(templates_with_action_files)
        print ('******** path', template_path)

        data = j.sal.fs.fileGetContents(template_path).splitlines()
        method_lines = [indx for indx in range(0, len(data)-1) if data[indx].startswith('    def ')]
        random_method_line = random.choice(method_lines)
        print ('******** line', random_method_line)
        random_method = data[random_method_line].split('def')[1].strip().split('(')[0]
        first_run = self.aysrepo.getRun(action=random_method)
        # first_run.execute()

        print ('******** method', random_method)
        data[random_method_line+1] = '%s # testing changing the template' % data[random_method_line+1]
        j.sal.fs.writeFile(template_path, '\n'.join(data))

        self.aysrepo._services = {}

        second_run = self.aysrepo.getRun(action=random_method)

        # check second_run only contains changed 
        # change 1 template method
        # ask for aysrun for init, check the aysrun is ok, right aysi impacted
        # do init
        # check that right ays were impacted and only the ones required (through state object)

    def test_change_1template_schema(self):
        if self.subname != "main":
            raise j.exceptions.Input("test only supported on main")

        # self.aysrepo.init()
        random_blueprint = random.choice(self.aysrepo.blueprints)
        blueprint_templates = [key.split('__')[0] for model in random_blueprint.models for key in model]

        templates_with_schema = [self.aysrepo.getTemplate(template).path_hrd_schema for template in blueprint_templates if j.sal.fs.exists(self.aysrepo.getTemplate(template).path_hrd_schema)]
        schema_path = random.choice(templates_with_schema)
        print ('******** path', schema_path)

        first_run = self.aysrepo.getRun(action='install')
        first_run.execute()
        original = j.sal.fs.fileGetContents(schema_path)
        j.sal.fs.writeFile(schema_path, '\nextra.param = type:str default:\'test\'\n', append=True)
        self.aysrepo._services = {}

        second_run = self.aysrepo.getRun(action='install')

        assert first_run.steps != second_run.steps, "something's not right!"

        j.sal.fs.writeFile(schema_path, original)

        third_run = self.aysrepo.getRun(action='install')

        assert second_run.steps != third_run.steps, "No good"

        # change 1 template schema (add variable)
        # ask for aysrun for init, check the aysrun is ok, right aysi impacted
        # do init
        # check that right ays were impacted and only the ones required (through state object)
        # do now same for remove of variable

    def test_change_blueprint(self):
        if self.subname != "main":
            raise j.exceptions.Input("test only supported on main")
        random_blueprint = random.choice(self.aysrepo.blueprints)
        bp_path = random_blueprint.path

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
