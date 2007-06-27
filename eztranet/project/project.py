# -*- coding: utf-8 -*-
from zope.interface import implements
from zope.app.folder.folder import Folder
from zope.component import adapts, getAllUtilitiesRegisteredFor, adapter
from zope.app.folder.interfaces import IFolder
from zope.schema.interfaces import IVocabularyFactory, IVocabularyTokenized, ISource
from zope.component.interface import nameToInterface, interfaceToName
from zope.schema.vocabulary import SimpleTerm
from zope.interface.declarations import alsoProvides, noLongerProvides
from zope.proxy import removeAllProxies
from zope.app.container.interfaces import INameChooser, IObjectRemovedEvent, IObjectAddedEvent, IObjectRemovedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.app.container.contained import NameChooser
from zope.app.container.btree import BTreeContainer
from zope.component.factory import Factory
from zope.app.component.hooks import getSite
from zope.app.file.file import File
from zope.app.file.image import Image
from zope.app.file.interfaces import IImage
from persistent import Persistent
import os
import PIL.Image
from StringIO import StringIO
from tempfile import NamedTemporaryFile, TemporaryFile
from interfaces import *
from flashpreview import compute_flashvideo
from eztranet.thumbnail.interfaces import IThumbnail

class ProjectContainer(BTreeContainer):
  "a project container"
  implements(IProjectContainer)
  __name__=__parent__=None

ProjectContainerFactory = Factory(ProjectContainer)
    
class Project(BTreeContainer):
    implements(IProject)
    title=u""
    description=u""
    __name__=__parent__=None
    def __init__(self, title=None, description=None):
        self.title, self.description = title, description
        super(Project, self).__init__()

ProjectFactory = Factory(Project)

class ProjectItem(Persistent):
    implements(IProjectItem)
    title=u""
    description=u""
    __name__=__parent__=None
    def __init__(self, title=None, description=None):
        self.title = title
        self.description = description
        super(ProjectItem, self).__init__()

ProjectItemFactory = Factory(ProjectItem)

class ProjectNameChooser(NameChooser):
    u"""
    adapter that allows to choose the __name__ of a project
    """
    adapts(IProjectContainer)
    implements(INameChooser)
    def chooseName(self, name, project):
        if name:
            return name
        if project is not None and len(project.title)>0:
            rawname = project.title
            newname = unicode.lower(rawname).strip().replace(' ','-').replace(u'/',u'-').lstrip('+@')
            return newname
        raise "ProjectNameChooser Error"


class ProjectItemNameChooser(NameChooser):
    u"""
    adapter that allows to choose the __name__ of a projectitem
    """
    adapts(IProject)
    implements(INameChooser)
    def chooseName(self, name, projectitem):   
        if name:
            return name
        if projectitem is not None and len(projectitem.title)>0:
            rawname = projectitem.title
            newname = unicode.lower(rawname).strip().replace(' ','-').replace(u'/',u'-').lstrip('+@')
            return newname
        raise "ProjectItemNameChooser Error"

class ProjectImage(ProjectItem, Image):
    implements(IProjectImage)
    __parent__ = __name__ = None
    title = description = u""

class ProjectVideo(ProjectItem, File):
    implements(IProjectVideo)
    __parent__ = __name__ = None
    title = description = u""
    flash_video = flash_video_tempfile = None
        
class SearchableTextOfProject(object):
    u"""
    l'adapter qui permet d'indexer les projects
    """
    adapts(IProject)
    implements(ISearchableTextOfProject)
    def __init__(self, context):
        self.context = context
    def getSearchableText(self):
        sourcetext = texttoindex = self.context.title + " " + self.context.description
        for word in sourcetext.split():        
            for subword in [ word[i:] for i in xrange(len(word)) if len(word)>=1 ]:
                texttoindex += subword + " "
        return texttoindex

class SearchableTextOfProjectItem(object):
    u"""
    l'adapter qui permet d'indexer les projects
    """
    adapts(IProjectItem)
    implements(ISearchableTextOfProjectItem)
    def __init__(self, context):
        self.context = context
    def getSearchableText(self):
        sourcetext = texttoindex = self.context.title + " " + self.context.description
        for word in sourcetext.split():        
            for subword in [ word[i:] for i in xrange(len(word)) if len(word)>=1 ]:
                texttoindex += subword + " "
        return texttoindex


class ProjectThumbnail(object):
    u"adapter from a project to a thumbnail"
    adapts(IProject)
    implements(IThumbnail)
    image = None
    url = '/@@/folder.png'
    def __init__(self, context):
        self.context = context
    def compute_thumbnail(self):
        pass

@adapter(IProjectImage)
def ProjectImageThumbnailer(image):
    u"thumbnail creator for ProjectImage"
    tmp=StringIO()
    i = PIL.Image.open(StringIO(image.data))
    i.thumbnail((150,150))
    i.save(tmp, "png")
    return tmp.getvalue()

@adapter(IProjectVideo)
def ProjectVideoThumbnailer(video):
    u"thumbnail creator for ProjectVideo"
    u"convert the video to png, without audio, with only 1 frame, with a delay of 3 seconds"
    tmpfile = NamedTemporaryFile()
    tmpfile.write(video.data)
    tmpfile.flush()
    thumbnail = os.popen("ffmpeg -i %s -vcodec png -ss 3 -vframes 1 -an -f rawvideo -" % tmpfile.name).read()
    tmpfile.close()
    return ProjectImageThumbnailer(Image(thumbnail))

@adapter(IProjectVideo, IObjectAddedEvent)
def ProjectVideoAdded(video, event):
    u"warning, here the object is NOT security proxied"
    video.flash_video_tempfile = compute_flashvideo(video)

@adapter(IProjectVideo, IObjectModifiedEvent)
def ProjectVideoModified(video, event):
    u"warning, here the object IS security proxied"
    if event.descriptions and 'data' in event.descriptions[0].attributes:
        # we compute the flash video only if we uploaded something
        video.flash_video_tempfile = compute_flashvideo(video)

@adapter(IProjectVideo, IObjectRemovedEvent)
def ProjectVideoRemoved(video, event):
    tmpfile = video.flash_video_tempfile
    for file in tmpfile, tmpfile+".OK", tmpfile+'.FAILED': 
        if os.path.exists(file):
            os.remove(file)
