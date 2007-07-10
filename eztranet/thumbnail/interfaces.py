# -*- coding: utf-8 -*-
from zope.interface import Interface, Attribute

class IThumbnailed(Interface):
    u"""
    The marker interface to put on an object that must have a thumbnail
    """


class IThumbnail(Interface):
    u"""
    interface offered by an object that has a thumbnail.
    Implementations can decide to provides either the thumbnail, or the URL,
    or both.
    'url' is good for static resource images (to be cached),
    'image' can be used for a generated thumbnail that have no view nor URL
    """
    image = Attribute("The Image object corresponding to the thumbnail")
    url = Attribute("The URL of a thumbnail")
    def compute_thumbnail():
        pass

class IThumbnailer(Interface):
    u"""
    The interface under which are registered specific thumbnailer utilities
    """