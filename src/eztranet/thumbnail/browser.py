from interfaces import IThumbnail
from os.path import join, dirname
from zope.component import queryAdapter, getAdapter
from zope.file.download import Display
from zope.interface import Interface
from zope.publisher.browser import BrowserView
from zope.security.proxy import removeSecurityProxy
from zope.traversing.browser.absoluteurl import absoluteURL
import zope.app.file
import zope.app.publisher
import zope.file

class ThumbnailImageView(BrowserView):
    """The thumbnail view of an object"""

    def __call__(self):
        #TODO check this
        thumbnail = removeSecurityProxy(IThumbnail(self.context))
        # if we have a thumbnail, return it
        if zope.file.interfaces.IFile.providedBy(thumbnail.image):
            return Display(thumbnail.image, self.request)()
        if zope.app.file.interfaces.IImage.providedBy(thumbnail.image):
            return thumbnail.image.data
        # if we don't, return the default thumbnail
        if thumbnail.image is None and thumbnail.resource is not None:
            image = queryAdapter(self.request, interface=Interface, name=thumbnail.resource)
            if image is not None:
                return image.GET()
        # otherwise, return a hardcoded default thumbnail
        return open(join(dirname(__file__), 'default_thumbnail.png')).read()


class ThumbnailUrlView(BrowserView):
    """The view that provides an URL for the thumbnail of an object.

    On the model of the absolute_url view.
    (for static thumbnails such as thumbnails for folders,
    so that they are cached by the browser)
    """

    def __call__(self):
        thumbnail = removeSecurityProxy(IThumbnail(self.context)) #TODO check this
        if thumbnail.image is not None:
            return absoluteURL(self.context, self.request) + "/@@thumbnail_image"
        if thumbnail.resource is not None:
            return '/@@/%s' % thumbnail.resource
        return "/@@/default_thumbnail.png"


