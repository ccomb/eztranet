# -*- coding: utf-8 -*-
import os, string
from threading import Thread, Timer
from tempfile import mkstemp
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import Interface, implements
from zope.component import adapts
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.traversing.api import getPath
from zope.proxy import removeAllProxies

class FlashConverterThread(Thread):
    u"""
    The thread that runs ffmpeg and write the result video file
    The name of the file gives the status of the compression
    """
    def __init__(self, origname, targetname):
        self.origname, self.targetname = origname, targetname
        super(FlashConverterThread, self).__init__()
    def run(self):
        if os.spawnlp(os.P_WAIT, 'ffmpeg', 'ffmpeg', '-i', self.origname, '-ar', '22050', self.targetname):
            os.remove(self.origname)
            open(self.targetname+".FAILED", 'a').close() #touch
            return
        os.remove(self.origname)
        os.rename(self.targetname, self.targetname+".OK")


def compute_flashvideo(video):
    tmpfile, tmpname = mkstemp()
    os.write(tmpfile, video.data)
    os.close(tmpfile)
    t = FlashConverterThread(tmpname, tmpname + ".flv")
    t.start()
    return tmpname + ".flv"
    

class FlashContentProvider(object):
    implements(IContentProvider)
    adapts(Interface, IDefaultBrowserLayer, Interface)
    def __init__(self, context, request, view):
        self.context, self.request, self.view = context, request, view
    def update(self):
        context = removeAllProxies(self.context)
        status_or_file = context.flash_video_tempfile
        if status_or_file != None and status_or_file != 'OK' and status_or_file != 'FAILED':
            if os.path.exists(context.flash_video_tempfile+".OK"):
                flvname = context.flash_video_tempfile+".OK"
                flvfile = open(flvname)
                context.flash_video = flvfile.read()
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
            return """
<object id="flowplayer" type="application/x-shockwave-flash" data="/@@/flowplayer.swf" width="640" height="480">
	<param name="allowScriptAccess" value="sameDomain" />
	<param name="movie" value="/@@/flowplayer.swf" />
	<param name="quality" value="high" />
	<param name="scale" value="noScale" />
	<param name="wmode" value="transparent" />
    <param name="flashvars" value="config={ initialScale:'orig', videoFile: '../%s/@@flv', loop: false }" />
</object>
""" % getPath(self.context)
        else:        
            return "Compressing..."