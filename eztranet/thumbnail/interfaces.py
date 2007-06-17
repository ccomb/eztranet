# -*- coding: utf-8 -*-
from zope.interface import Interface, Attribute
from zope.app.file.interfaces import IImage

class IThumbnailed(Interface):
    u"""
    The marker interface to put on an object that must have a thumbnail
    """


class IThumbnail(Interface):
    u"""
    interface offered by an object that has a thumbnail.
    This is the same interface as an Image object
    """
    thumbnail = Attribute("the thumbnail of the object")
    def compute_thumbnail():
        pass

class IThumbnailer(Interface):
    u"""
    The interface under which are registered specific thumbnailer utilities
    """