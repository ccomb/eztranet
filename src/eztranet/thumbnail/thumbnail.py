# -*- coding: utf-8 -*-
from StringIO import StringIO
from subprocess import Popen, PIPE
from zope.annotation.interfaces import IAnnotations
from zope.app.container.interfaces import IObjectAddedEvent, IContainer
from zope.component import adapts, adapter, queryAdapter
from zope.file.file import File
from zope.file.interfaces import IFile
from zope.interface import implements
from zope.lifecycleevent.interfaces import IObjectModifiedEvent, IObjectCopiedEvent
from zope.publisher.browser import FileUpload
from zope.security.proxy import removeSecurityProxy
import PIL.Image
import transaction

from eztranet.config.interfaces import IConfig, IConfigurable
from interfaces import IThumbnail, IThumbnailed, IThumbnailer, IThumbnailConfig

CONFIG_KEY = 'eztranet.thumbnail'
SIZE_CONFIG_KEY = 'eztranet.thumbnail.size'

class Thumbnail(object):
    u"""
    The adapter from any object to IThumbnail
    """
    implements(IThumbnail)
    adapts(IThumbnailed)
    resource = None

    def __init__(self, context):
        self.context = self.__parent__ = context

    def _get_image(self):
        return IAnnotations(self.context).get(CONFIG_KEY)

    def _set_image(self, data):
        if data is not None:
            blob = IAnnotations(self.context)[CONFIG_KEY] = File()
            if type(data) is str:
                file = blob.open('w')
                file.write(data)
                file.close()
            elif type(data) is FileUpload:
                blob._data.consumeFile(data.name)
            else:
                raise TypeError('bad image data')
        else:
            IAnnotations(self.context)[CONFIG_KEY] = None

    image = property(_get_image, _set_image)

    def compute_thumbnail(self):
        # remove the previous thumbnail
        self.image = None
        # retrieve the config for the thumbnail size
        size = None
        config = queryAdapter(self.context, IConfig, default=None)
        if config is not None:
            size = config.get_config(SIZE_CONFIG_KEY)
        if type(size) is not int:
            size = 120
        # we get the named adapter (the name is the major mimeType)
        name = getattr(self.context, 'mimeType', u'').split('/')[0]
        thumbnailer = queryAdapter(removeSecurityProxy(self.context),
                                   IThumbnailer,
                                   name)
        if thumbnailer is not None:
            # compute the thumbnail
            thumbnail_content = thumbnailer(size)
            if thumbnail_content is not None:
                self.image = thumbnail_content
                self.image.mimeType = 'image/jpeg'


class BaseThumbnailer(object):
    """
    base class for specific thumbnailers
    """
    implements(IThumbnailer)
    adapts(IFile)

    def __init__(self, context):
        self.context = context

class ImageThumbnailer(BaseThumbnailer):
    """
    thumbnail creator for an Image.
    This must be registered as a named adapter for IFile.
    The name corresponds to the major contentType: 'image'
    """
    def __call__(self, size=120):
        tmp=StringIO()
        try:
            fd = self.context.open()
            i = PIL.Image.open(fd)
            i.thumbnail((size, size), PIL.Image.ANTIALIAS)
            i.save(tmp, "jpeg")
            fd.close()
            return tmp.getvalue()
        except IOError:
            return None

class VideoThumbnailer(BaseThumbnailer):
    """
    thumbnail creator for a Video.
    This must be registered as a named adapter for IFile.
    The name corresponds to the major contentType: 'video'
    It converts the video to png, without audio, with only 1 frame,
    at an offset of 3 seconds, then convert to jpeg with the ImageThumbailer
    """
    def __call__(self, size=120):
        blobfile = self.context.open()
        p = Popen("ffmpeg -i %s -y -vcodec png -ss 3 -vframes 1 -an -f rawvideo -" % blobfile.name,
                  shell=True, stderr=PIPE, stdout=PIPE)
        thumbnail_content = p.stdout.read()
        err = p.stderr.read()
        if len(thumbnail_content) == 0: # maybe there is less than 3 seconds?
            p = Popen("ffmpeg -i %s -y -vcodec png -vframes 1 -an -f rawvideo -" % blobfile.name,
                      shell=True, stderr=PIPE, stdout=PIPE)
            thumbnail_content = p.stdout.read()
            err = p.stderr.read()
        blobfile.close()
        thumbfile = File()
        fd = thumbfile.open('w')
        fd.write(thumbnail_content)
        fd.close()
        return ImageThumbnailer(thumbfile)(size)


@adapter(IThumbnailed, IObjectModifiedEvent)
def ThumbnailedModified(obj, event):
    if (event.descriptions
        and hasattr(event.descriptions[0],'attributes')
        and 'data' in event.descriptions[0].attributes
       ):
        IThumbnail(obj).compute_thumbnail()


@adapter(IThumbnailed, IObjectAddedEvent)
def ThumbnailedAdded(video, event):
    """
    warning, here the object is NOT security proxied
    """
    IThumbnail(video).compute_thumbnail()


@adapter(IThumbnailed, IObjectCopiedEvent)
def ThumbnailedCopied(obj, event):
    IThumbnail(obj).compute_thumbnail()


class ThumbnailConfig(object):
    """adapter for the config form"""
    implements(IThumbnailConfig)
    adapts(IConfigurable)

    def __init__(self, context):
        # __parent__ is needed for trusted adapters
        self.__parent__ = self.context = context

    def _get_size(self):
        return IConfig(self.context).get_config(SIZE_CONFIG_KEY)

    def _set_size(self, size):
        IConfig(self.context).set_config(SIZE_CONFIG_KEY, size)

    size = property(_get_size, _set_size)

    def _get_recompute(self):
        pass

    def _set_recompute(self, value):
        if value == True:
            # recursively recompute thumbnails
            self.__recursive_recompute(self.context)

    def __recursive_recompute(self, obj):
        if IContainer.providedBy(obj):
            for o in obj:
                self.__recursive_recompute(obj[o])
        elif IThumbnailed.providedBy(obj):
            IThumbnail(obj).compute_thumbnail()


    recompute = property(_get_recompute, _set_recompute)



