from Asker import ConsoleAsker, TelegramAsker
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

    def getBot(self, bot_updater):
        asker = TelegramAsker(bot_updater)
        deployer = CockpitDeployer(asker)
        deployer.type = 'bot'
        return deployer
