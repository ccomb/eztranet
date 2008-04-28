from zope.interface import Interface, Attribute
from zope.schema import Int
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('eztranet')

class IFlashPreviewable(Interface):
    u"marker interface that offers a flash preview for a video file"

class IFlashPreviewParams(Interface):
    """
    interface to manage the parameters of the flash preview
    """
    bitrate = Int(title=_(u'bitrate (kb/s)'),
                  description=_(u'encoding bitrate of the video'))
    width = Int(title=_(u'width (px)'),
                  description=_(u'encoding bitrate of the video'))
    height = Int(title=_(u'height (px)'),
                  description=_(u'encoding bitrate of the video'))


class IFlashPreview(Interface):
    """
    The interface used to access the flashpreview
    """
    flash_movie = \
        Attribute(_(u'the flash movie blob, or compressed temporary filename'))

    def encode( ):
        """
        encode the movie using parameters and store it as a blob.
        """
