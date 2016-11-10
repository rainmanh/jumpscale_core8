from tests.utils.utils import BaseTest
from ast import literal_eval

class InstallationTests(BaseTest):

    def setUp(self):
        super(InstallationTests, self).setUp()
        self.run_cmd_via_subprocess('cd tests/testsuite/js_installation; bash docker.sh {} {}'
                                    .format(self.user, self.password))

    def test001_install_js8(self):
        """ JS-001
        *Test case for checking JumpScale8 installation.*

        **Test Scenario:**

        #. Check needed packages.
        #. Pull docker image to be used for JumpScale installation.
        #. Create a container to install JumpScale on it.
        #. Update the docker and install JumpScale
        #. Check if js is working, should succeed
        #. Check if directories under /optvar/ is as expected
        #. check if directories under /opt/jumpscale8/ is as expected
        #. Compare js.dir to j.tools.cuisine.local.core.dir_paths, should be the same
        #.
        """
        self.lg('%s STARTED' % self._testID)

        self.lg('Check needed packages')
        if not self.check_package('docker.io'):
            self.run_cmd_via_subprocess('apt-get install docker.io')

        self.lg('Pull docker image to be used for jumpscale installation')
        self.run_cmd_via_subprocess('docker pull kheirj/ssh-docker:V3')

        self.lg('Create a container to install JumpScale on it')
        #self.run_cmd_via_subprocess('docker run -d -t -i --name=js --hostname=js kheirj/ssh-docker:V3')

        self.lg('update the docker and install jumpscale8')
        self.execute_command_on_docker('js', 'apt-get update')
        self.execute_command_on_docker('js', 'echo Y | apt-get install curl')
        self.execute_command_on_docker('js', 'curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/'
                                             '{}/install/install.sh > install.sh'.format(self.branch))
        if self.branch != "master":
            self.execute_command_on_docker('js', 'export JSBRANCH = "{}"'.format(self.branch))
        self.execute_command_on_docker('js', 'bash install.sh')

        # Validation steps
        self.lg('Check if js is working, should succeed')
        response = self.execute_command_on_docker('js', 'js "print(j.sal.fs.getcwd())"')
        self.assertEqual(response, '/\n')

        self.lg('Check if directories under /optvar/ is as expected')
        response = self.execute_command_on_docker('js', 'ls /optvar')
        self.assertEqual(response,'cfg\ndata\n')

        self.lg('Check if directories under /opt/jumpscale8/ is as expected')
        response = self.execute_command_on_docker('js', 'ls /opt/jumpscale8/')
        self.assertEqual(response, 'bin\nenv.sh\nlib\n')

        self.lg('Compare js.dir to j.tools.cuisine.local.core.dir_paths, should be the same')
        response = self.execute_command_on_docker('js', 'js "print(j.dirs)"')
        response2 = self.execute_command_on_docker('js', 'js "print(j.tools.cuisine.local.core.dir_paths)"')
        dict1 = self.convert_string_to_dict(response, '\n')
        dict2 = literal_eval(response2)
        self.assertEqual(dict1['homeDir'], dict2['homeDir'])
        self.assertEqual(dict1['base'], dict2['base'])
        #slash diff
        #import ipdb; ipdb.sset_trace()
        self.assertEqual(dict1['appDir'].replace('/',''), dict2['appDir'].replace('/',''))
        self.assertEqual(dict1['libDir'].replace('/',''), dict2['libDir'].replace('/',''))
        self.assertEqual(dict1['binDir'].replace('/',''), dict2['binDir'].replace('/',''))
        self.assertEqual(dict1['cfgDir'].replace('/',''), dict2['cfgDir'].replace('/',''))
        self.assertEqual(dict1['codeDir'].replace('/', ''), dict2['codeDir'].replace('/', ''))
        self.assertEqual(dict1['jsLibDir'].replace('/', ''), dict2['jsLibDir'].replace('/', ''))
        #Failed assertions
        self.assertEqual(dict1['pidDir'], dict2['pidDir'])
        self.assertEqual(dict1['tmpDir'], dict2['tmpDir'])
        self.assertEqual(dict1['tmplsDir'], dict2['tmplsDir'])
        self.assertEqual(dict1['logDir'], dict2['logDir'])
        self.assertEqual(dict1['varDir'], dict2['varDir'])

        #self.lg('remove the docker container')
        #self.run_cmd_via_subprocess("docker rm -f js")

        self.lg('%s ENDED' % self._testID)


