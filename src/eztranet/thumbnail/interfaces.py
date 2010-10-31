from zope.annotation.interfaces import IAttributeAnnotatable
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface, Attribute
from zope.schema import Int, Bool, Bytes
_ = MessageFactory('eztranet')

from eztranet.config.interfaces import IConfigForm
from eztranet.project.interfaces import LargeBytes

class IThumbnailed(IAttributeAnnotatable):
    """The marker interface to put on an object that must have a thumbnail"""


class IThumbnail(Interface):
    """Interface offered by an object that has a thumbnail.
    """

    image = LargeBytes(title=_(u'Thumbnail'),
                  description=_(u'The Image object corresponding to the thumbnail'),
                  required=False)

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

