# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope.publisher.browser import BrowserView
from zope.location.interfaces import ILocation
from tempfile import NamedTemporaryFile
import os

class DownloadView(BrowserView):
    u"""
    The view that allows to download any downloadable content
    """
    def __call__(self):
        filename = "filecontent"
        print type(self.context)
        if ILocation.providedBy(self.context):
            filename = self.context.__name__
        tmpfile = NamedTemporaryFile()
        tmpfile.write(self.context.data)
        tmpfile.flush()
        self.request.response.setHeader('Content-disposition', 'attachment; filename=%s' % filename)
        self.request.response.setHeader('Content-length', os.path.getsize(tmpfile.name))
        return tmpfile.file


