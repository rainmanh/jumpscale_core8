from Asker import ConsoleAsker, TelegramAsker
from CockpitBot import CockpitDeployerBot
from JumpScale.clients.cockpit.CockpitDeployer import CockpitDeployer

class CockpitFactory:
    def __init__(self):
        self.__jslocation__ = "j.clients.cockpit"
        self.installer = Installer()


class Installer:

    def getCLI(self):
        asker = ConsoleAsker()
        deployer = CockpitDeployer(asker)
        deployer.type = 'cli'
        return deployer

    def getBot(self):
        bot = CockpitDeployerBot()
        return bot
