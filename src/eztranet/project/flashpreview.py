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
import urllib

class FlashConverterThread(Thread):
    u"""
    The thread that runs ffmpeg and write the result video file
    The name of the file gives the status of the compression
    """
    def __init__(self, origname, targetname):
        self.origname, self.targetname = origname, targetname
        super(FlashConverterThread, self).__init__()
    def run(self):
        if os.spawnlp(os.P_WAIT, 'ffmpeg', 'ffmpeg', '-i', self.origname, '-ar', '22050', '-b', '512k', '-g', '240', self.targetname):
            os.remove(self.origname)
            open(self.targetname+".FAILED", 'a').close() #touch
            return
        os.remove(self.origname)
        os.rename(self.targetname, self.targetname+".OK")

def compute_flashvideo(video):
    tmpfile, tmpname = mkstemp()
    os.write(tmpfile, video.open().read())
    os.close(tmpfile)
    t = FlashConverterThread(tmpname, tmpname + ".flv")
    t.start()
    return tmpname + ".flv"
    
