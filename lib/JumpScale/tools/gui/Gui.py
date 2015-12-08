
from .dialog.EasyDialog import EasyDialog
from .dialog.EasyDialogWizardForm import EasyDialogWizardForm

class Gui:
    def __init__(self):
        self.__jslocation__ = "j.tools.gui"
        self.dialog = EasyDialog()
        self.form = EasyDialogWizardForm()
