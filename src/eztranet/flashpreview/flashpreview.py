import os
from threading import Thread
from tempfile import mkstemp
from zope.interface import implements
from zope.component import adapts
from zope.file.interfaces import IFile
from interfaces import IFlashPreview
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict

class FlashPreview(object):
    implements(IFlashPreview)
    adapts(IFile)

    def __init__(self, file):
        self.context = file
        annotations = IAnnotations(self.context)
        if 'eztranet.flashpreview' not in annotations:
            annotations['eztranet.flashpreview'] = PersistentDict()
        if 'preview' not in annotations['eztranet.flashpreview']:
            annotations['eztranet.flashpreview']['preview'] = None

    def encode(self):
        """
        start encoding and return the thread
        """
        tmpfile, tmpname = mkstemp()
        os.write(tmpfile, self.context.open().read())
        os.close(tmpfile)
        thread = FlashConverterThread(tmpname, tmpname + ".flv")
        thread.start()
        IAnnotations(self.context)['eztranet.flashpreview']['preview'] = tmpname + ".flv"
        return thread

    def get_flash_movie(self):
        return IAnnotations(self.context)['eztranet.flashpreview']['preview']

    def set_flash_movie(self, file):
        IAnnotations(self.context)['eztranet.flashpreview']['preview'] = file

    flash_movie = property(get_flash_movie, set_flash_movie)

class FlashConverterThread(Thread):
    """
    The thread that runs ffmpeg and write the resulting video file
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
        
