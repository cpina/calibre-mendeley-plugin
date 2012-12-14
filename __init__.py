import os

from calibre.customize import InterfaceActionBase

class MendeleyPlugin(InterfaceActionBase):
    name = 'Mendeley Plugin Importer'
    description = 'Imports your Mendeley library into Calibre'
    supported_platforms = ['linux'] # not tested on Windows and osx
    author = 'Carles Pina'
    version = (1, 0, 0)
    minimum_calibre_version = (0, 9, 0) # not tested with previous ones

    #: This field defines the GUI plugin class that contains all the code
    #: that actually does something. Its format is module_path:class_name
    #: The specified class must be defined in the specified module.
    actual_plugin = 'calibre_plugins.mendeley_to_calibre.ui:Mendeley'

    def is_customizable(self):
        return True

    def config_widget(self):
        from calibre_plugins.mendeley_to_calibre import ConfigWidget
	return ConfigWidget(self.actual_plugin_)

    def save_settings(self, config_widget):
        config_widget.save_settings()
