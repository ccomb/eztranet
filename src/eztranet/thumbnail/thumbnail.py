# -*- coding: utf-8 -*-
from zope.interface import implements
from zope.component import adapts, adapter, queryAdapter
from zope.app.container.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.annotation.interfaces import IAnnotations
from zope.file.interfaces import IFile
from zope.file.file import File
from zope.security.proxy import removeSecurityProxy
from interfaces import IThumbnail, IThumbnailed, IThumbnailer
import PIL.Image
from StringIO import StringIO
import os

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
        # we get the named adapter (the name is the major mimeType)
        name = u''
        if hasattr(self.context, 'mimeType'):
            name = self.context.mimeType.split('/')[0]
        thumbnailer = queryAdapter(removeSecurityProxy(self.context),
                                   IThumbnailer,
                                   name)
        if thumbnailer is not None:
            thumbnail_content = thumbnailer()
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
    def __call__(self):
        tmp=StringIO()
        try:
            fd = self.context.open()
            i = PIL.Image.open(fd)
            i.thumbnail((120,120), PIL.Image.ANTIALIAS)
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
    def __call__(self):
        blobpath = self.context._data._current_filename()
        thumbnail_content = os.popen("ffmpeg -i %s -y -vcodec png -ss 3 -vframes 1 -an -f rawvideo -" % blobpath).read()
        if len(thumbnail_content) == 0: # maybe there is less than 3 seconds?
            thumbnail_content = os.popen("ffmpeg -i %s -y -vcodec png -vframes 1 -an -f rawvideo -" % blobpath).read()
        thumbfile = File()
        fd = thumbfile.open('w')
        fd.write(thumbnail_content)
        fd.close()
        return ImageThumbnailer(thumbfile)()

@adapter(IThumbnailed, IObjectModifiedEvent)
def ThumbnailedModified(obj, event):
    if event.descriptions \
    and hasattr(event.descriptions[0],'attributes') \
    and 'data' in event.descriptions[0].attributes:
        IThumbnail(obj).compute_thumbnail()

@adapter(IThumbnailed, IObjectAddedEvent)
def ThumbnailedAdded(video, event):
    """
    warning, here the object is NOT security proxied
    """
    IThumbnail(video).compute_thumbnail()
