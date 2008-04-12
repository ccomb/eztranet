# -*- coding: utf-8 -*-
import os
from threading import Thread
from tempfile import mkstemp
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import Interface, implements
from zope.component import adapts
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.security.proxy import removeSecurityProxy
from zope.traversing.browser.absoluteurl import AbsoluteURL
from zope.file.file import File
import urllib

class FlashContentProvider(object):
    implements(IContentProvider)
    adapts(Interface, IDefaultBrowserLayer, Interface)
    def __init__(self, context, request, view):
        self.context, self.request, self.view = context, request, view
    def update(self):
        context = removeSecurityProxy(self.context)
        status_or_file = context.flash_video_tempfile
        if status_or_file != None and status_or_file != 'OK' and status_or_file != 'FAILED':
            if os.path.exists(context.flash_video_tempfile+".OK"):
                flvname = context.flash_video_tempfile+".OK"
                flvfile = open(flvname)
                context.flash_video = File()
                openfile = context.flash_video.open('w')
                openfile.write(flvfile.read())
                openfile.close()
                flvfile.close()
                os.remove(flvname)
                context.flash_video_tempfile = 'OK'
            if os.path.exists(context.flash_video_tempfile+".FAILED"):
                os.remove(context.flash_video_tempfile+".FAILED")
                context.flash_video_tempfile = 'FAILED'
    def render(self):
        if self.context.flash_video_tempfile == 'FAILED':
            return u"La compression flash a échoué.<br/>Vous pouvez néanmoins télécharger la vidéo d'origine."
        if self.context.flash_video_tempfile == 'OK':
            return u"""
<object id="flowplayer" type="application/x-shockwave-flash" data="/@@/flowplayer.swf" width="720" height="540">
	<param name="allowScriptAccess" value="sameDomain" />
	<param name="movie" value="/@@/flowplayer.swf" />
	<param name="quality" value="high" />
	<param name="scale" value="noScale" />
	<param name="wmode" value="transparent" />
    <param name="flashvars" value="config={ initialScale:'orig', baseURL: '%s/', videoFile: '@@flv', loop: false }" />
</object>
""" % urllib.quote(AbsoluteURL(self.context, self.request)().encode('utf-8'))
        else:        
            return "<br/><br/>En cours de compression..."
