from zope.interface import Interface
from zope.interface.interfaces import IInterface
from zope.annotation.interfaces import IAttributeAnnotatable

class IConfigurable(IAttributeAnnotatable):
    """marker interface for an object that can have a configuration"""

class IConfig(Interface):
    """Offers some config for a persistent object, stored in the annotations"""

    def get_config(key):
        """get the config value corresponding to the key"""

    def set_config(key, value):
        """set the value for the key in the config"""

class IConfigForm(Interface):
    """the base interface for config forms"""

class IConfigFormType(IInterface):
    """interface type for the config forms"""
