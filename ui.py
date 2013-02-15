#!/usr/bin/env python

# "THE CHOCOLATE-WARE LICENSE" (Revision 1):
# <carles@pina.cat> wrote this file. As long as you retain
# this notice you can do whatever you want with this stuff. If we meet some
# day, and you think this stuff is worth it, you can buy me a chocolate in
# return.
# (license based in Beer-ware, see
#           https://fedoraproject.org/wiki/Licensing/Beerware )

__license__   = 'ChocolateWare r1'
__copyright__ = '2012, 2013, Carles Pina Estany'

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
