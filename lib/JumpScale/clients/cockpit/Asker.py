from JumpScale import j
from telegram.dispatcher import run_async
import queue

class ConsoleAsker(object):
    """Asker interface with console"""
    def __init__(self):
        super(ConsoleAsker, self).__init__()

    def ask_repo_url(self):
        def validate(input):
            return j.sal.nettools.checkUrlReachable(input)
        repo_url = j.tools.console.askString("Url of the git repository where to store the ays repo of your cockpit. The repo need to exists", retry=3, validate=validate)
        return repo_url

    def ask_ovc_url(self):
        def validate(input):
            try:
                j.sal.nettools.checkUrlReachable(input)
                return True
            except:
                return False
        ovc_url = j.tools.console.askString("Url of the Gener8 where to deploy your cockpit. e.g: 'be-conv-2.demo.greenitglobe.com'", retry=3, validate=validate)
        return ovc_url

    def ask_ovc_login(self):
        def validate(input):
            return True
        login = j.tools.console.askString("Login of your account on the Gener8 where to deploy cockpit", retry=3, validate=validate)
        return login

    def ask_ovc_password(self):
        def validate(input):
            return True
        passwd = j.tools.console.askPassword("Password of your account on the Gener8 where to deploy cockpit", confirm=True, retry=3, validate=validate)
        return passwd

    def ask_ovc_vdc(self):
        def validate(input):
            return True
        name = j.tools.console.askString("Name of the Virtual Data center where to deploy the G8Cockpit", defaultparam='cockpit', regex=None, retry=3, validate=validate)
        return name

    def ask_ovc_account(self, ovc_client=None):
        """
        ovc_client: if ovc client is given.
            first check if only one account is available, if so don't ask anything and just return the account
            If multiple account, ask with proposition.
            If no ovc_client, accept any entry
        """
        if ovc_client:
            if len(ovc_client.accounts) == 1:
                account = ovc_client.accounts[0]
                account_name = account.model['name']
            elif len(ovc_client.accounts) > 1:
                choices = [acc.model['name'] for acc in ovc_client.accounts]
                account_name = j.tools.console.askChoice(choices, descr='Choose which account to use', sort=False, maxchoice=len(choices), height=len(choices) * 10, autocomplete=True)
            return account_name

        # if not ovc_client or accounts number is 0
        def validate(input):
            return True
        account_name = j.tools.console.askString("Account to use on the G8 wherre to deploy the cockpit", defaultparam='', regex=None, retry=3, validate=validate)
        return account_name

    def ask_ovc_location(self, ovc_client=None, account_name=None, vdc_name=None):
        """
        ovc_client: if ovc client is given.
            first check if only one location is available, if so don't ask anything and just return the location
            If multiple location,
                if accoutn_name and vdc_name are given, automaticly retrieve location base on the name of the vdc
                if not account_name and vdc_name, ask to choose between all available locations
            If no ovc_client, accept any entry
        """
        if ovc_client:
            if len(ovc_client.locations) == 1:
                return ovc_client.locations[0]['name']
            elif account_name and vdc_name:
                if account_name in ovc_client.accounts:
                    account = ovc_client.accounts[account_name]
                    if vdc_name in account.spaces:
                        return account.spaces[vdc_name].model['location']
            elif len(ovc_client.locations) > 1:
                choices = [loc.model['name'] for loc in ovc_client.locations]
                location = j.tools.console.askChoice(choices, descr='Choose which location to use', sort=False, maxchoice=len(choices), height=len(choices) * 10, autocomplete=True)
                return location

        # if not ovc_client or locations number is 0
        def validate(input):
            return True
        location = j.tools.console.askString("Location of the vdc choosen", defaultparam='', regex=None, retry=3, validate=validate)
        return location

    def ask_dns_login(self):
        def validate(input):
            return True
        login = j.tools.console.askString("Login of your account on the DNS cluster", retry=3, validate=validate)
        return login

    def ask_dns_password(self):
        def validate(input):
            return True
        passwd = j.tools.console.askPassword("Password of your account on the DNS cluster", confirm=True, retry=3, validate=validate)
        return passwd

    def ask_domain(self):
        def validate(input):
            return True
        domain = j.tools.console.askString("Domaine to use for your cockpit", defaultparam='', retry=3, validate=validate)
        return domain

    def ask_ssh_key(self):
        def validate(input):
            key = j.do.getSSHKeyFromAgentPub(input, die=False)
            return (key is not None)
        key = j.tools.console.askString("Name of the ssh key to authorize on the G8Cockpit. key are fetch from ssh-agent.", defaultparam='id_rsa', retry=3, validate=validate)
        return key

    def ask_portal_password(self):
        def validate(input):
            if len(input) < 6:
                return False
            return True
        passwd = j.tools.console.askPassword("Admin password for the portal (6 characters minumum)", confirm=True, retry=3, validate=validate)
        return passwd

    def ask_expose_ssh(self):
        return j.tools.console.askYesNo("Do you want to expose SSH over http using shellinabox")

    def ask_bot_token(self):
        def validate(input):
            return True
        msg = """
AtYourService Robot creation
Please connect to telegram and talk to @botfather.
execute the command /newbot and choose a name and username for your bot
@botfather should give you a token, paste it here please :"""
        token = j.tools.console.askString(msg, defaultparam='', retry=3, validate=validate)

        msg = """
add command description to your bot.
type '/setcommands' in @botfather, choose your bot and past these lines :

start - create your private environment
project - manage your project (create, list, remove)
blueprint - manage your blueprints project (list, get, remove)
ays - perform some atyourservice actions on your project
help - show you what I can do"""
        print(msg)
        resp = j.tools.console.askYesNo("is it done ?")
        while not resp:
            print("please do it")
            resp = j.tools.console.askYesNo("is it done ?")
        return token

    def ask_gid(self):
        def validate(input):
            return j.data.types.int.check(input)
        gid = j.tools.console.askString("Grid ID to give to the controller. Need to be an integer", defaultparam=1, retry=3, validate=validate)
        return gid


class TelegramAsker(object):
    """Asker Interface with telegram"""
    # TODO implement retry on ask* Methods

    def __init__(self, updater):
        super(TelegramAsker, self).__init__()
        self.chat_id = None
        self.updater = updater
        self.bot = self.updater.bot
        self.last_question_id = None
        self.queue = queue.Queue(maxsize=1)

        self._register_handlers()

    def _register_handlers(self):
        self.updater.dispatcher.addTelegramMessageHandler(self.handlerChoice)

    def say(self, msg):
        self.bot.sendMessage(chat_id=self.chat_id, text=msg)

    @run_async
    def handlerChoice(self, bot, update, **kwargs):
        print('enter handler choise')
        if not self.last_question_id:
            print("[-] No question has been asked, we should not end up here")
            return
        if update.message.message_id != self.last_question_id+1:
            print("[-] Message id (%d) is not the response to the last question od (%d)" % (update.message_id, self.last_question_id))
            return
        self.queue.put(update.message.text)

    def askYesNo(self, message):
        custom_keyboar = [['yes', 'no']]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboar, resize_keyboard=True, one_time_keyboard=True)
        message = self.bot.sendMessage(chat_id=self.chat_id, text=message, parse_mode="Markdown", reply_markup=reply_markup)
        self.last_question_id = message.message_id
        value = self.queue.get()
        self.last_question_id = None
        return value

    def askChoice(self, message, choices):
        custom_keyboar = []
        for i in range(0, len(choices), 2):
            custom_keyboar.append(choices[i:i+2])
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboar, resize_keyboard=True, one_time_keyboard=True)
        message = self.bot.sendMessage(chat_id=self.chat_id, text=message, parse_mode="Markdown", reply_markup=reply_markup)
        self.last_question_id = message.message_id
        value = self.queue.get()
        self.last_question_id = None
        return value

    def askString(self, message):
        message = self.bot.sendMessage(chat_id=self.chat_id, text=message, parse_mode="Markdown")
        self.last_question_id = message.message_id
        value = self.queue.get()
        self.last_question_id = None
        return value


    def ask_repo_url(self):
        repo_url = self.askString("Url of the git repository where to store the ays repo of your cockpit. The repo need to exists")
        return repo_url

    def ask_ovc_url(self):
        def validate(input):
            return j.sal.nettools.checkUrlReachable(input)
        ovc_url = self.askString("Url of the Gener8 where to deploy your cockpit. e.g: 'be-conv-2.demo.greenitglobe.com'")
        return ovc_url

    def ask_ovc_login(self):
        def validate(input):
            return True
        login = self.askString("Login of your account on the Gener8 where to deploy the cockpit")
        return login

    def ask_ovc_password(self):
        def validate(input):
            return True
        passwd = self.askString("Password of your account on the Gener8 where to deploy cockpit")
        return passwd

    def ask_ovc_vdc(self):
        def validate(input):
            return True
        name = self.askString("Name of the Virtual Data center where to deploy the G8Cockpit")
        return name

    def ask_ovc_account(self, ovc_client=None):
        """
        ovc_client: if ovc client is given.
            first check if only one account is available, if so don't ask anything and just return the account
            If multiple account, ask with proposition.
            If no ovc_client, accept any entry
        """
        if ovc_client:
            if len(ovc_client.accounts) == 1:
                account = ovc_client.accounts[0]
                accoutn_name = account.model['name']
            elif len(ovc_client.accounts) > 1:
                choices = [acc.model['name'] for acc in ovc_client.accounts]
                accoutn_name = self.askChoice('Choose which account to use', choices)
            return accoutn_name

        # if not ovc_client or accounts number is 0
        def validate(input):
            return True
        accoutn_name = self.askString("Account to use on the G8 wherre to deploy the cockpit")
        return accoutn_name

    def ask_ovc_location(self, ovc_client=None, account_name=None, vdc_name=None):
        """
        ovc_client: if ovc client is given.
            first check if only one location is available, if so don't ask anything and just return the location
            If multiple location,
                if accoutn_name and vdc_name are given, automaticly retrieve location base on the name of the vdc
                if not account_name and vdc_name, ask to choose between all available locations
            If no ovc_client, accept any entry
        """
        if ovc_client:
            if len(ovc_client.locations) == 1:
                return ovc_client.locations[0]['name']
            elif account_name and vdc_name:
                if account_name in ovc_client.accounts:
                    account = ovc_client.accounts[account_name]
                    if vdc_name in account.spaces:
                        return account.spaces[vdc_name].model['location']
            elif len(ovc_client.locations) > 1:
                choices = [loc.model['name'] for loc in ovc_client.locations]
                location = j.tools.console.askChoice('Choose which location to use', choices)
                return location

        # if not ovc_client or locations number is 0
        def validate(input):
            return True
        location = self.askString("Location of the vdc choosen")
        return location

    def ask_dns_login(self):
        def validate(input):
            return True
        login = self.askString("Login of your account on the DN")
        return login

    def ask_dns_password(self):
        def validate(input):
            return True
        passwd = self.askString("Password of your account on the DNS cluster")
        return passwd

    def ask_domain(self):
        def validate(input):
            return True
        domain = self.askString("Domaine to use for your cockpit")
        return domain

    def ask_ssh_key(self):
        def validate(input):
            key = j.do.getSSHKeyFromAgentPub(input, die=False)
            return (key is not None)
        key = self.askString("Name of the ssh key to authorize on the G8Cockpit. key are fetch from ssh-agent.")
        return key

    def ask_portal_password(self):
        def validate(input):
            if len(input) < 6:
                return False
            return True
        passwd = self.askString("Admin password for the portal (6 characters minumum)")
        return passwd

    def ask_expose_ssh(self):
        return self.askYesNo("Do you want to expose SSH over http using shellinabox")

    def ask_bot_token(self):
        def validate(input):
            return True
        msg = """
"AtYourService Robot creation
"Please connect to telegram and talk to @botfather.
"execute the command /newbot and choose a name and username for your bot
"@botfather should give you a token, paste it here please :
"""
        token = self.askString(msg)
        msg = """add command description to your bot.
type '/setcommands' in @botfather, choose your bot and past these lines :
start - create your private environment
project - manage your project (create, list, remove)
blueprint - manage your blueprints project (list, get, remove)
ays - perform some atyourservice actions on your project
help - show you what I can do"""
        resp = self.askYesNo("is it done ?")
        while not resp:
            print("please do it")
            resp = self.askYesNo("is it done ?")
        return token

    def ask_gid(self):
        def validate(input):
            return j.data.types.int.check(input)
        gid = self.askString("Grid ID to give to the controller. Need to be an integer")
        return gid
