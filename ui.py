#!/usr/bin/env python

from calibre.gui2.actions import InterfaceAction
from calibre_plugins.bbcgf_ebook.main import BBCGFDialog

class Mendeley(InterfaceAction):
    name = 'Mendeley Plugin'

    action_spec = ('this is some text', None, 'this is some other text', ())

    def genesis(self):
        print 'Genesis is called'
        pass

    def show_dialog(self):
        base_plugin_object = self.interface_action_base_plugin
	do_user_config = base_plugin_object.do_user_config
	d = BBCGFDialog(self.gui, self.qaction.icon(), do_user_config)
	d.show()
