# -*- coding: utf-8 -*-
from zope.publisher.browser import BrowserView
from zope.app.file.browser.image import ImageData
from zope.traversing.browser.absoluteurl import absoluteURL

from interfaces import *

class ThumbnailImageView(BrowserView, ImageData):
    u"""
    The thumbnail view of an object
    """
    def __call__(self):
        u"""A full day to find this single line:
        We must change the context here and not in the __init__ !
        """
        thumbnail = IThumbnail(self.context)
        if thumbnail.image is not None:
            self.context = thumbnail.image
            return self.show()
        return None

class ThumbnailUrlView(BrowserView):
    u"""
    The view that provides an URL for the thumbnail of an object.
    (for static thumbnails, so that they are cached by the browser
    """
    def __call__(self):
        thumbnail = IThumbnail(self.context)
        if thumbnail.url is not None:
            return thumbnail.url
        if thumbnail.image is not None:
            return absoluteURL(self.context, self.request) + "/@@thumbnail_image"
        return "/@@/default_thumbnail.png"
