from interfaces import IFlashPreview, IFlashPreviewable
from persistent.dict import PersistentDict
from tempfile import mkstemp
from zc.async.interfaces import IQueue
from zc.async.job import Job
from zope.annotation.interfaces import IAnnotations
from zope.app.container.interfaces import IObjectRemovedEvent, IObjectAddedEvent
from zope.component import adapts, adapter
from zope.file.interfaces import IFile
from zope.file.file import File
from zope.interface import implements
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
import os
import subprocess

class FlashPreview(object):
    """Adapter that get or set the flash preview of a video file"""

    implements(IFlashPreview)
    adapts(IFile)

    def __init__(self, file):
        self.context = self.__parent__ = file
        annotations = IAnnotations(self.context)
        if 'eztranet.flashpreview' not in annotations:
            annotations['eztranet.flashpreview'] = PersistentDict()
        if 'preview' not in annotations['eztranet.flashpreview']:
            annotations['eztranet.flashpreview']['preview'] = None

    def encode(self):
        """start encoding and return the thread"""
        # target path
        target_fd, target_path = mkstemp('.flv')
        os.close(target_fd)
        # queue
        queue = IQueue(self.context)
        job = queue.put(Job(video_converter, self, target_path))
        IAnnotations(self.context)['eztranet.flashpreview']['preview'] = job
        return job

    def get_flash_movie(self):
        return IAnnotations(self.context)['eztranet.flashpreview']['preview']

    def set_flash_movie(self, file):
        IAnnotations(self.context)['eztranet.flashpreview']['preview'] = file

    flash_movie = property(get_flash_movie, set_flash_movie)


def video_converter(obj, target_path):
    """The function that runs ffmpeg and write the resulting video file"""
    # source
    with obj.context.open() as sourcefile:
        retcode = subprocess.call(['ffmpeg', '-i', sourcefile.name, '-y',
                                   '-ar', '22050',
                                   '-b', '800k',
                                   '-g', '240',
                                   target_path],
                                   stderr=subprocess.PIPE,
                                   stdout=subprocess.PIPE)
    if retcode == 1:
        # compression failed
        os.remove(target_path)
        return False
    elif retcode == 0:
        # compression succeeded
        if os.path.exists(target_path):
            obj.flash_movie = File()
            obj.flash_movie._data.consumeFile(target_path)
        return True


@adapter(IFlashPreviewable, IObjectAddedEvent)
def FlashPreviewableAdded(video, event):
    """warning, here the object is NOT security proxied
    """
    IFlashPreview(video).encode()


@adapter(IFlashPreviewable, IObjectModifiedEvent)
def FlashPreviewableModified(video, event):
    """warning, here the object IS security proxied
    """
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

