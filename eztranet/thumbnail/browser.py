# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope.publisher.browser import BrowserView, BrowserPage
from zope.app.file.browser.image import ImageData
from zope.app.file.image import Image
from zope.location.interfaces import ILocation
import os

from interfaces import *

class ThumbnailView(BrowserView, ImageData):
    u"""
    The thumbnail view of an object
    """
    def __call__(self):
        u"""A full day to find this single line:
        We must change the context here and not in the __init__ !
        """
        self.context = IThumbnail(self.context).thumbnail
        return self.show()

