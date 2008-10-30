from zope.publisher.browser import BrowserView
from zope.location.interfaces import ILocation
from tempfile import TemporaryFile

class DownloadView(BrowserView):
    u"""
    The view that allows to download any downloadable content
    """
    def __call__(self):
        filename = "filecontent"
        if ILocation.providedBy(self.context):
            filename = self.context.__name__
        tmpfile = TemporaryFile()
        tmpfile.write(self.context.data)
        tmpfile.seek(0)
        self.request.response.setHeader('Content-disposition', 'attachment; filename="%s"' % filename.encode('utf-8'))
        self.request.response.setHeader('Content-length', self.context.getSize())
        self.request.response.setHeader('Content-Type', self.context.contentType)
        return tmpfile.read()


