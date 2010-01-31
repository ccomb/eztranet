from eztranet.flashpreview.interfaces import IFlashPreview
from z3c.layer.pagelet import IPageletBrowserLayer
from zope.component import adapts
from zope.contentprovider.interfaces import IContentProvider
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface, implements
from zope.security.proxy import removeSecurityProxy
from zope.traversing.browser.absoluteurl import AbsoluteURL
import os
import urllib
import zope.file
_ = MessageFactory('eztranet')


class FlashContentProvider(object):
    implements(IContentProvider)
    adapts(Interface, IPageletBrowserLayer, Interface)
    def __init__(self, context, request, view):
        self.context, self.request, self.view = context, request, view
    def update(self):
        self.flashpreview = removeSecurityProxy(IFlashPreview(self.context))

    def render(self):
        if type(self.flashpreview.flash_movie) is str:
            if self.flashpreview.flash_movie == 'FAILED':
                return _(u'Flash compression failed.<br/>\
                           However you can still download the original movie.')
            elif self.flashpreview.flash_movie[0:4] == '/tmp':
                return _(u'<br/><br/>Currently compressing... \
                          (<a href=".">click to reload</a>)')
        else:
            return u'''<a href="%s/@@flv" style="display:block;width:720px;height:576px" id="player">
                       </a>
                       <script>
                         flowplayer("player", "/@@/flowplayer.swf", {
                            plugins: { controls: {url: '/@@/flowplayer.controls.swf'} }
                         });
                       </script>
                    ''' % urllib.quote(AbsoluteURL(self.context, self.request)().encode('utf-8'))


class FlvView(zope.file.download.Download):
    """
    view to get the flv file stored in the annotations
    """
    def __init__(self, context, request):
        super(FlvView, self).__init__(context, request)
        self.flashpreview = removeSecurityProxy(IFlashPreview(context))

    def __call__(self):
        return zope.file.download.Download(self.flashpreview.flash_movie, self.request)()


class FlowPlayerHeader(object):
    """Content provider for the js header of the flowplayer"""

    def update(self):
        pass

    def render(self):
        return '<script type="text/javascript" src="/@@/flowplayer.js"></script>'
