from zope.component import adapts
from zope.interface import implements
from interfaces import IConfigurable, IConfig
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict

ANNOTATION_KEY = 'eztranet.config'

class Config(object):
    """adapter that offers the configuration"""

    adapts(IConfigurable)
    implements(IConfig)

    def __init__(self, adapted_object):
        self.context = adapted_object

    def _get_config(self, obj, key):
        """recursive method that watches parents"""
        config = None
        try:
            config = IAnnotations(obj)[ANNOTATION_KEY][key]
        except KeyError:
            if hasattr(obj, '__parent__') and obj.__parent__ is not None:
                config = self._get_config(obj.__parent__, key)
        return config

    def get_config(self, key):
        """retrieve the config from the annotations

        If it is not available in the current object,
        watch the parent recursively
        """
        return self._get_config(self.context, key)

    def set_config(self, key, value):
        """write the configuration in the annotations of the current object"""
        annotations = IAnnotations(self.context)
        if ANNOTATION_KEY not in annotations:
            annotations[ANNOTATION_KEY] = PersistentDict()
        if value is None:
            del annotations[ANNOTATION_KEY][key]
        else:
            annotations[ANNOTATION_KEY][key] = value

