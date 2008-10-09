import os
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import Interface, implements
from zope.component import adapts
from z3c.layer.pagelet import IPageletBrowserLayer
from zope.traversing.browser.absoluteurl import AbsoluteURL
from zope.file.file import File
from eztranet.flashpreview.interfaces import IFlashPreview
from zope.security.proxy import removeSecurityProxy
import urllib
import zope.file
import transaction
from zope.i18nmessageid import MessageFactory
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
            return u"""
<object id="flowplayer" type="application/x-shockwave-flash" data="/@@/flowplayer.swf" width="720" height="576">
	<param name="allowScriptAccess" value="sameDomain" />
	<param name="movie" value="/@@/flowplayer.swf" />
	<param name="quality" value="high" />
	<param name="scale" value="noScale" />
	<param name="wmode" value="transparent" />
    <param name="flashvars" value="config={ initialScale:'fit',
                                            baseURL: '%s/',
                                            videoFile: '@@flv',
                                            loop: false,
                                            backgroundColor: -1,
                                            controlBarBackgroundColor: 0x6C77AE,
                                            useNativeFullScreen: false,
                                            autoRewind: true,
                                            controlBarGloss: 'high',
                                            menuItems: [ true, true, true, true, true, false, false ] }" />
</object>
""" % urllib.quote(AbsoluteURL(self.context, self.request)().encode('utf-8'))


class FlvView(zope.file.download.Download):
    """
    view to get the flv file stored in the annotations
    """
    def __init__(self, context, request):
        super(FlvView, self).__init__(context, request)
        self.flashpreview = removeSecurityProxy(IFlashPreview(context))

    def __call__(self):
        return zope.file.download.Download(self.flashpreview.flash_movie, self.request)()


