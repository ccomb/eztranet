from eztranet.flashpreview.interfaces import IFlashPreview
from z3c.layer.pagelet import IPageletBrowserLayer
from zope.component import adapts
from zope.contentprovider.interfaces import IContentProvider
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface, implements
from zope.security.proxy import removeSecurityProxy
from zope.traversing.browser.absoluteurl import AbsoluteURL
from zc.async.interfaces import PENDING, COMPLETED, ACTIVE, ASSIGNED
from zc.async.interfaces import IJob
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
        if IJob.providedBy(self.flashpreview.flash_movie):
            if self.flashpreview.flash_movie.status in [PENDING, ASSIGNED]:
                return _(u'<br/><br/>Compression pending \
                          (<a href=".">click to reload</a>)')
            elif self.flashpreview.flash_movie.status == ACTIVE:
                return _(u'<br/><br/>Currently compressing... \
                          (<a href=".">click to reload</a>)')
            elif self.flashpreview.flash_movie.status == COMPLETED:
                return _(u'Flash compression failed.<br/>\
                           However you can still download the original movie.')
            else : return self.flashpreview.flash_movie.status
        else:
            rooturl = self.request.getApplicationURL()
            return u'''<a href="%s/@@flv" style="display:block;width:720px;height:576px" id="player">
                       </a>
                       <script>
                         flowplayer("player", "%s/%%2B%%2Bresource%%2B%%2Bflowplayer.swf", {
                            clip: { scaling: 'fit' },
                            plugins: { controls: {url: '%s/%%2B%%2Bresource%%2B%%2Bflowplayer.controls.swf'} },
                         });
                       </script>
                    ''' % (AbsoluteURL(self.context, self.request)().encode('utf-8'), rooturl, rooturl)


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
        return '<script type="text/javascript" src="/++resource++flowplayer.js"></script>'
