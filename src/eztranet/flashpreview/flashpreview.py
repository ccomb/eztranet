import os
from threading import Thread
from tempfile import mkstemp
from zope.interface import implements
from zope.component import adapts, adapter
from zope.file.interfaces import IFile
from interfaces import IFlashPreview, IFlashPreviewable
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
from zope.app.container.interfaces import IObjectRemovedEvent, IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
import transaction

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
        transaction.commit() # to be able to open the blob later
        target_tmp = mkstemp()
        thread = FlashConverterThread(self.context, target_tmp)
        thread.start()
        IAnnotations(self.context)['eztranet.flashpreview']['preview'] = target_tmp[1]
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
    def __init__(self, sourcefile, target_tmp):
        self.sourcefile = sourcefile
        self.targetfd, self.targetpath = target_tmp
        super(FlashConverterThread, self).__init__()
    def run(self):
        fd = self.sourcefile.open()
        if os.spawnlp(os.P_WAIT, 'ffmpeg', 'ffmpeg', '-i', fd.name, '-y',
                                                     '-ar', '22050',
                                                     '-b', '800k',
                                                     '-g', '240',
                                                     self.targetpath + '.flv'):
            fd.close()
            os.close(self.targetfd)
            os.rename(self.targetpath, self.targetpath+".FAILED")
            return
        fd.close()
        os.close(self.targetfd)
        os.remove(self.targetpath)
        os.rename(self.targetpath + '.flv', self.targetpath+".OK")
        
@adapter(IFlashPreviewable, IObjectAddedEvent)
def FlashPreviewableAdded(video, event):
    """
    warning, here the object is NOT security proxied
    """
    IFlashPreview(video).encode()

@adapter(IFlashPreviewable, IObjectModifiedEvent)
def FlashPreviewableModified(video, event):
    "warning, here the object IS security proxied"
    try:
        if 'data' in event.descriptions[0].attributes:
            # we compute the flash video only if we uploaded something
            IFlashPreview(video).encode()
    except:
        return

@adapter(IFlashPreviewable, IObjectRemovedEvent)
def FlashPreviewableRemoved(video, event):
    tmpfile = IFlashPreview(video).flash_movie
    if type(tmpfile) is str and tmpfile[0:4] == '/tmp':
        for file in tmpfile, tmpfile+".OK", tmpfile+'.FAILED': 
            if os.path.exists(file):
                os.remove(file)

