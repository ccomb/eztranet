# -*- coding: utf-8 -*-
from zope.interface import implements
from zope.component import adapts, queryAdapter, getAdapter, adapter
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.annotation.interfaces import IAnnotations
from zope.app.file.image import Image
from zope.proxy import removeAllProxies
from interfaces import *

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
            self.compute_thumbnail()
        self.image = IAnnotations(context)['eztranet.thumbnail']

    def compute_thumbnail(self):
        try:
            thumbnail = getAdapter(removeAllProxies(self.context), IThumbnailer)
        except:
            thumbnail = None
        if thumbnail is not None:
            self.image = IAnnotations(self.context)['eztranet.thumbnail'] = Image(thumbnail)


@adapter(IThumbnailed, IObjectModifiedEvent)
def ThumbnailedModified(object, event):
    if event.descriptions and 'data' in event.descriptions[0].attributes:
        IThumbnail(object).compute_thumbnail()