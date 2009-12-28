from __future__ import with_statement
from contextlib import contextmanager
from interfaces import IExport
from z3c.menu.simple.menu import SimpleMenuItem
from z3c.pagelet.browser import BrowserPagelet
from zope.component import getAdapter
from zope.i18nmessageid import MessageFactory
from zope.publisher.browser import BrowserView
import os, tempfile

_ = MessageFactory('eztranet')

class ExportPage(BrowserPagelet):
    """Page to export a folder as a zip file
    This page should display a selection form to choose the export format.
    The export format would be generated from the registered export utilities,
    and transmitted via a POST argument.
    We first export only as a zip file.
    """

@contextmanager
def autoclean(somefile):
    yield somefile
    somefile.close()
    os.remove(somefile.name)


class ExportDownload(BrowserView):
    """the actual view that creates and returns the zip file
    """
    filename = None
    def __call__(self):
        if 'do_export' not in self.request:
            return self.request.response.redirect('.')
        #choose a temp path to export
        fd, self.filename = tempfile.mkstemp()
        os.close(fd)
        export_adapter = getAdapter(self.context, IExport, 'zip')
        export_adapter.do_export(self.filename)

        self.request.response.setHeader(
                'Content-disposition',
                'attachment; filename="%s"' % (self.context.__name__ + '.zip').encode('utf-8'))
        filesize = os.stat_result(os.stat(self.filename)).st_size
        self.request.response.setHeader('Content-length',
                                        filesize)
        self.request.response.setHeader('Content-Type', 'application/zip')
        with autoclean(open(self.filename)) as zipfile:
            return zipfile.read()



class ExportPageMenuItem(SimpleMenuItem):
    title = _(u'Export')
    url = 'export.html'
    weight = 900

