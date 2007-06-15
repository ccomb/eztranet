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
from zope.app.container.interfaces import INameChooser
from zope.app.container.contained import NameChooser
from zope.app.container.btree import BTreeContainer
from zope.component.factory import Factory
from zope.app.component.hooks import getSite
from zope.app.file.file import File
from zope.app.file.image import Image
from zope.app.file.interfaces import IImage
from persistent import Persistent
import string, os
from tempfile import NamedTemporaryFile
from interfaces import *


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
    implements(INameChooser)
    adapts(IProject)
    def chooseName(self, name, project):
        if not name and project is None:
            raise "ProjectNameChooser Error"
        if name:
            rawname = name
        if project is not None and len(project.title)>0:
            rawname = project.title
        return string.lower(rawname).strip().replace(' ','-').replace(u'/',u'-').lstrip('+@')


class ProjectItemNameChooser(NameChooser):
    u"""
    adapter that allows to choose the __name__ of a projectitem
    """
    implements(INameChooser)
    adapts(IProjectItem)
    def chooseName(self, name, projectitem):
        if not name and projectitem is None:
            raise "ProjectItemNameChooser Error"
        if name:
            rawname = name
        if projectitem is not None and len(projectitem.title)>0:
            rawname = projectitem.title
        return string.lower(rawname).strip().replace(' ','-').replace(u'/',u'-').lstrip('+@')


class ProjectImage(Image, ProjectItem):
    __parent__=__name__=None
    title=description=u""
    implements(IProjectImage)

class ProjectVideo(File, ProjectItem):
    __parent__=__name__=None
    title=description=u""
    implements(IProjectVideo)

class SearchableTextOfProject(object):
    u"""
    l'adapter qui permet d'indexer les projects
    """
    implements(ISearchableTextOfProject)
    adapts(IProject)
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
    implements(ISearchableTextOfProjectItem)
    adapts(IProjectItem)
    def __init__(self, context):
        self.context = context
    def getSearchableText(self):
        sourcetext = texttoindex = self.context.title + " " + self.context.description
        for word in sourcetext.split():        
            for subword in [ word[i:] for i in xrange(len(word)) if len(word)>=1 ]:
                texttoindex += subword + " "
        return texttoindex

@adapter(IProjectImage)
def ProjectImageThumbnailer(image):
    return image.data
    
@adapter(IProjectVideo)
def ProjectVideoThumbnailer(video):
    u"faudrait faire ça dans un thread"
    tmpfile = NamedTemporaryFile()
    tmpfile.write(video.data)
    tmpfile.flush()
    thumbnail = os.popen("ffmpeg -i %s -vcodec png -vframes 1 -an -f rawvideo -" % tmpfile.name).read()
    tmpfile.close()
    return thumbnail

