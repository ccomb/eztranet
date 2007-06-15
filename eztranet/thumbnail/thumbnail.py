# -*- coding: utf-8 -*-
from zope.interface import implements
from zope.component import adapts, queryAdapter
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
    thumbnail = None
    def __init__(self, context):
        self.context = self.__parent__ = context
        if 'eztranet.thumbnail' not in IAnnotations(context):
            self.thumbnail = IAnnotations(context)['eztranet.thumbnail'] = None
        self.thumbnail = IAnnotations(context)['eztranet.thumbnail']
        if self.thumbnail is None:
            self._compute_thumbnail()
    def _compute_thumbnail(self):
        self.thumbnail = Image()
        thumbnail = queryAdapter(removeAllProxies(self.context), IThumbnailer)
        if thumbnail is not None:
            self.thumbnail = IAnnotations(self.context)['eztranet.thumbnail'] = Image(thumbnail)
        else:
            raise NotImplementedError, "Objects that want to provide a thumbnail must provide an IThumbnailer adapter."
