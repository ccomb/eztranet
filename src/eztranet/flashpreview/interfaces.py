# -*- coding: utf-8 -*-
from zope.interface import Interface, Attribute
from zope.schema import Int

class IFlashPreviewable(Interface):
    u"marker interface that offers a flash preview for a video file"

class IFlashPreviewParams(Interface):
    """
    interface to manage the parameters of the flash preview
    """
    bitrate = Int(title = u'bitrate (kb/s)',
                  description = u'encoding bitrate of the video')
    width = Int(title = u'width (px)',
                  description = u'encoding bitrate of the video')
    height = Int(title = u'height (px)',
                  description = u'encoding bitrate of the video')


class IFlashPreview(Interface):
    """
    The interface used to access the flashpreview
    """
    flash_movie = Attribute(u'the flash movie blob, or compressed temporary filename')

    def encode( ):
        """
        encode the movie using parameters and store it as a blob.
        """