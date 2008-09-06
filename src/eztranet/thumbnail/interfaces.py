from zope.schema import Int, Bool
from zope.interface import Interface, Attribute
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.i18nmessageid import MessageFactory
from eztranet.config.interfaces import IConfigForm
_ = MessageFactory('eztranet')

class IThumbnailed(IAttributeAnnotatable):
    """The marker interface to put on an object that must have a thumbnail"""


class IThumbnail(Interface):
    """Interface offered by an object that has a thumbnail.

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
    """The interface under which are registered specific thumbnailer utilities"""


class IThumbnailConfig(IConfigForm):
    """Interface of the overall configuration form for thumbnails"""

    size = Int(title = _(u'Thumbnail size'),
               description = _(u'The size of the thumbnail'),
               required = False,
               default = None,
               min = 1)

    recompute = Bool(title = _(u'Recompute thumbnails?'),
                     description = _(u'Allows to recompute all thumbnails in '
                                     u'the current folder'),
                     default = False)

