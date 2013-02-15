#!/usr/bin/env python

__license__   = 'GPL v3'
__copyright__ = '2012, Carles Pina'

from calibre.gui2.actions import InterfaceAction
from calibre_plugins.mendeley_to_calibre.main import MendeleyDialog

class Mendeley(InterfaceAction):
    name = 'Mendeley Plugin'

    action_spec = ('Import from Mendeley', None, 'Import from Mendeley', ())

    def genesis(self):
        icon = get_icons('images/mendeley.png')
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.show_dialog)

    def show_dialog(self):
        base_plugin_object = self.interface_action_base_plugin
        do_user_config = base_plugin_object.do_user_config
        d = MendeleyDialog(self.gui, self.qaction.icon(), do_user_config)
        d.show()
