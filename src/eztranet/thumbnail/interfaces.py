from zope.interface import Interface, Attribute
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('eztranet')

class IThumbnailed(IAttributeAnnotatable):
    """
    The marker interface to put on an object that must have a thumbnail
    """


class IThumbnail(Interface):
    """
    interface offered by an object that has a thumbnail.
    Implementations can decide to provides either the thumbnail, or the URL,
    or both.
    'url' is good for static resource images (to be cached),
    'image' can be used for a generated thumbnail that have no view nor URL
    """
    image = Attribute("The Image object corresponding to the thumbnail")
    url = Attribute(_(u'The URL of a thumbnail'))
    def compute_thumbnail(size):
        """compute a thumbnail with the given size"""

class IThumbnailer(Interface):
    """
    The interface under which are registered specific thumbnailer utilities
    """
