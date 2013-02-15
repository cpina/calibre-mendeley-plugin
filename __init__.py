# "THE CHOCOLATE-WARE LICENSE" (Revision 1):
# <carles@pina.cat> wrote this file. As long as you retain
# this notice you can do whatever you want with this stuff. If we meet some
# day, and you think this stuff is worth it, you can buy me a chocolate in
# return. - Carles Pina Estany
# (license based in Beer-ware, see
#           https://fedoraproject.org/wiki/Licensing/Beerware )

import os
from calibre.customize import InterfaceActionBase

class MendeleyPlugin(InterfaceActionBase):
    name = 'Mendeley Plugin Importer'
    description = 'Imports your Mendeley library into Calibre'
    supported_platforms = ['linux', 'windows', 'osx']
    author = 'Carles Pina'
    version = (0, 0, 1)
    minimum_calibre_version = (0, 9, 0) # not tested with previous ones

    #: This field defines the GUI plugin class that contains all the code
    #: that actually does something. Its format is module_path:class_name
    #: The specified class must be defined in the specified module.
    actual_plugin = 'calibre_plugins.mendeley_to_calibre.ui:Mendeley'

    def is_customizable(self):
        return True

    def config_widget(self):
        from calibre_plugins.mendeley_to_calibre.config import ConfigWidget
        return ConfigWidget(self.actual_plugin_)

    def save_settings(self, config_widget):
        config_widget.save_settings()
