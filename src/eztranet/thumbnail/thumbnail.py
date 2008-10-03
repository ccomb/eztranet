# -*- coding: utf-8 -*-
from zope.interface import implements
from zope.component import adapts, adapter, queryAdapter
from zope.app.container.interfaces import IObjectAddedEvent, IContainer
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.annotation.interfaces import IAnnotations
from zope.file.interfaces import IFile
from zope.file.file import File
from zope.security.proxy import removeSecurityProxy
from interfaces import IThumbnail, IThumbnailed, IThumbnailer, IThumbnailConfig
from eztranet.config.interfaces import IConfig, IConfigurable
import PIL.Image
from StringIO import StringIO
from subprocess import Popen, PIPE

SIZE_CONFIG_KEY = 'eztranet.thumbnail.size'

class Thumbnail(object):
    u"""
    The adapter from any object to IThumbnail
    """
    implements(IThumbnail)
    adapts(IThumbnailed)
    image = url = None
    def __init__(self, context):
        self.context = self.__parent__ = context
        if 'eztranet.thumbnail' not in IAnnotations(context):
            self.image = IAnnotations(context)['eztranet.thumbnail'] = None
            #self.compute_thumbnail()
        self.image = IAnnotations(context)['eztranet.thumbnail']

    def compute_thumbnail(self):
        # retrieve the config for the thumbnail size
        size = None
        config = queryAdapter(self.context, IConfig, default=None)
        if config is not None:
            size = config.get_config(SIZE_CONFIG_KEY)
        if type(size) is not int:
            size = 120
        # we get the named adapter (the name is the major mimeType)
        name = u''
        if hasattr(self.context, 'mimeType') and self.context.mimeType is not None:
            name = self.context.mimeType.split('/')[0]
        thumbnailer = queryAdapter(removeSecurityProxy(self.context),
                                   IThumbnailer,
                                   name)
        if thumbnailer is not None:
            thumbnail_content = thumbnailer(size)
            if thumbnail_content is not None:
                self.image = IAnnotations(self.context)['eztranet.thumbnail'] = File()
                file = self.image.open('w')
                file.write(thumbnail_content)
                file.close()
                self.url = None
            else:
                self.image = IAnnotations(self.context)['eztranet.thumbnail'] = None
                self.url = '/@@/default_thumbnail.png'
        else:
            self.image = IAnnotations(self.context)['eztranet.thumbnail'] = None
            self.url = '/@@/default_thumbnail.png'


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
            i.save(tmp, "png")
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
    at an offset of 3 seconds
    """
    def __call__(self, size=120):
        blobpath = self.context._data._current_filename()
        p = Popen("ffmpeg -i %s -y -vcodec png -ss 3 -vframes 1 -an -f rawvideo -" % blobpath,
                  shell=True, stderr=PIPE, stdout=PIPE)
        thumbnail_content = p.stdout.read()
        err = p.stderr.read()
        if len(thumbnail_content) == 0: # maybe there is less than 3 seconds?
            p = Popen("ffmpeg -i %s -y -vcodec png -vframes 1 -an -f rawvideo -" % blobpath,
                      shell=True, stderr=PIPE, stdout=PIPE)
            thumbnail_content = p.stdout.read()
            err = p.stderr.read()
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

class ThumbnailConfig(object):
    """adapter for the config form"""
    implements(IThumbnailConfig)
    adapts(IConfigurable)

    def __init__(self, context):
        self.context = context

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



