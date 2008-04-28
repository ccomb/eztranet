from zope.publisher.browser import BrowserView
from zope.file.download import Download
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.security.proxy import removeSecurityProxy
from interfaces import IThumbnail

class ThumbnailImageView(Download):
    """
    The thumbnail view of an object
    """
    def __call__(self):
        thumbnail = IThumbnail(self.context)
        if thumbnail.image is not None:
            return Download(removeSecurityProxy(thumbnail.image), self.request)()
        return None

class ThumbnailUrlView(BrowserView):
    """
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
