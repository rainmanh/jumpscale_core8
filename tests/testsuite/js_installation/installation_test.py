from tests.utils.utils import BaseTest
import os

class InstallationTests(BaseTest):

    def setUp(self):
        super(InstallationTests, self).setUp()
        os.system('cd tests/testsuite/js_installation; bash docker.sh {} {}'.format(self.user, self.password))

    def test001_install_js8(self):
        import ipdb;ipdb.sset_trace()
        self.lg('%s STARTED' % self._testID)

        self.lg('check packages')
        if not self.check_package('docker.io'):
            os.system('apt-get install docker.io')

        self.lg('pull docker image to be used for jumpscale installation')
        os.system('docker pull kheirj/ssh-docker:V3')

        self.lg('create container')
        os.system(' docker run -d -t -i --name=js --hostname=js kheirj/ssh-docker:V3')

        self.lg('update the docker and install jumpscale8')
        self.execute_command_on_docker('js', 'apt-get update')
        self.execute_command_on_docker('js', 'echo Y | apt-get install curl')
        self.execute_command_on_docker('js', 'curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/'
                                             '{}/install/install.sh > install.sh'.format(self.branch))
        if self.branch != "master":
            self.execute_command_on_docker('js', 'export JSBRANCH = "{}"'.format(self.branch))
        self.execute_command_on_docker('js', 'bash install.sh')


        # Validation steps
        self.lg('check if js is working, should succeed')
        response = self.execute_command_on_docker('js', 'js "print(1)"')
        self.assertEqual(response, '1\n')

        self.lg('check if directories under /optvar/ is as expected')
        response = self.execute_command_on_docker('js', 'ls /optvar')
        self.assertEqual(response,'cfg\ndata\n')

        self.lg('check if directories under /opt/jumpscale8/ is as expected')
        response = self.execute_command_on_docker('js', 'ls /opt/jumpscale8/')
        self.assertEqual(response, 'bin\nenv.sh\nlib\n')

        self.lg('remove the docker container')
        os.system("docker rm -f js")

        self.lg('%s ENDED' % self._testID)
