from zope.security.proxy import removeSecurityProxy
from zope.file.file import File
from interfaces import IFlashPreview, IFlashPreviewable
from persistent.dict import PersistentDict
from tempfile import mkstemp
from threading import Thread
from zope.annotation.interfaces import IAnnotations
from zope.app.container.interfaces import IObjectRemovedEvent, IObjectAddedEvent
from zope.component import adapts, adapter
from zope.file.interfaces import IFile
from zope.interface import implements
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
import os
import subprocess
import transaction

CHUNKSIZE = 1048576

class FlashPreview(object):
    """Adapter that get or set the flash preview of a video file"""

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
        """start encoding and return the thread"""

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
    """The thread that runs ffmpeg and write the resulting video file"""

    def __init__(self, sourcefile, target_tmp):
        self.sourcefile = sourcefile
        self.targetfd, self.targetpath = target_tmp
        super(FlashConverterThread, self).__init__()

    def run(self):
        fd = self.sourcefile.open()
        retcode = subprocess.call(['ffmpeg', '-i', fd.name, '-y',
                                             '-ar', '22050',
                                             '-b', '800k',
                                             '-g', '240',
                                             self.targetpath + '.flv'],
                                  stderr=subprocess.PIPE,
                                  stdout=subprocess.PIPE)
        transaction.begin()
        self.flashpreview = removeSecurityProxy(FlashPreview(self.sourcefile))
        if retcode == 1:
            # compression failed
            fd.close()
            os.close(self.targetfd)
            os.remove(self.targetpath)
            self.flashpreview.flash_movie = 'FAILED'
            transaction.commit()
            return
        elif retcode == 0:
            # compression succeeded
            fd.close()
            os.close(self.targetfd)
            if os.path.exists(self.targetpath):
                os.remove(self.targetpath)
            flvname = self.targetpath + '.flv'
            flvfile = open(flvname)
            self.flashpreview.flash_movie = File()
            openfile = self.flashpreview.flash_movie.open('w')
            chunk = flvfile.read(CHUNKSIZE)
            while chunk:
                openfile.write(chunk)
                chunk = flvfile.read(CHUNKSIZE)
            openfile.close()
            flvfile.close()
            transaction.commit()
            os.remove(flvname)


@adapter(IFlashPreviewable, IObjectAddedEvent)
def FlashPreviewableAdded(video, event):
    """warning, here the object is NOT security proxied"""

    IFlashPreview(video).encode()


@adapter(IFlashPreviewable, IObjectModifiedEvent)
def FlashPreviewableModified(video, event):
    """warning, here the object IS security proxied"""
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

