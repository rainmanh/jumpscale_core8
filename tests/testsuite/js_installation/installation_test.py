from tests.utils.utils import BaseTest
from ast import literal_eval
import time

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
        self.run_cmd_via_subprocess('docker run -d -t -i --name=js --hostname=js kheirj/ssh-docker:V3')

        self.lg('Update the docker and install jumpscale8')
        time.sleep(5)
        self.execute_command_on_docker('js', 'apt-get update')
        self.execute_command_on_docker('js', 'echo Y | apt-get install curl')
        self.execute_command_on_docker('js', 'curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/'
                                             '{}/install/install.sh > install.sh'.format(self.branch))
        if self.branch != "master":
            self.execute_command_on_docker('js', 'export JSBRANCH = "{}"'.format(self.branch))
        self.execute_command_on_docker('js', 'bash install.sh')
        time.sleep(50)
        
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
        self.assertEqual(dict1['HOMEDIR'], dict2['HOMEDIR'])
        self.assertEqual(dict1['base'], dict2['base'])
        #slash diff
        self.assertEqual(dict1['JSAPPDIR'].replace('/',''), dict2['JSAPPDIR'].replace('/',''))
        self.assertEqual(dict1['LIBDIR'].replace('/',''), dict2['LIBDIR'].replace('/',''))
        self.assertEqual(dict1['binDir'].replace('/',''), dict2['binDir'].replace('/',''))
        self.assertEqual(dict1['JSCFGDIR'].replace('/',''), dict2['JSCFGDIR'].replace('/',''))
        self.assertEqual(dict1['CODEDIR'].replace('/', ''), dict2['CODEDIR'].replace('/', ''))
        self.assertEqual(dict1['jsLibDir'].replace('/', ''), dict2['jsLibDir'].replace('/', ''))
        self.assertEqual(dict1['PIDDIR'].replace('/', ''), dict2['PIDDIR'].replace('/', ''))
        self.assertEqual(dict1['LOGDIR'].replace('/', ''), dict2['LOGDIR'].replace('/', ''))
        self.assertEqual(dict1['VARDIR'].replace('/', ''), dict2['VARDIR'].replace('/', ''))
        self.assertEqual(dict1['TEMPLATEDIR'].replace('/', ''), dict2['TEMPLATEDIR'].replace('/', ''))

        #self.lg('remove the docker container')
        #self.run_cmd_via_subprocess("docker rm -f js")

        self.lg('%s ENDED' % self._testID)


