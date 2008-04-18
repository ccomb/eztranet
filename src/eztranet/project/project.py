from zope.interface import implements, implementsOnly
from zope.component import adapts, adapter
from zope.app.container.interfaces import INameChooser, \
                                          IObjectRemovedEvent, \
                                          IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.app.container.contained import NameChooser
from zope.app.container.btree import BTreeContainer
from zope.component.factory import Factory
from zope.file.file import File
import os
from interfaces import IProjectContainer, IProjectItem, IProject, \
                                          IProjectImage, IProjectVideo, \
                        ISearchableTextOfProject, ISearchableTextOfProjectItem
from eztranet.thumbnail.interfaces import IThumbnail, IThumbnailer
from eztranet.flashpreview.interfaces import IFlashPreview

class ProjectContainer(BTreeContainer):
  """
  a project container
  """
  implements(IProjectContainer)
  __name__ = __parent__ = None

ProjectContainerFactory = Factory(ProjectContainer)
    
class Project(BTreeContainer):
    implements(IProject)
    __name__ = __parent__ = None

    def __init__(self, title=u'', description=u''):
        super(Project, self).__init__( )
        self.title = title
        self.description = description

ProjectFactory = Factory(Project)

class ProjectItem(File):
    """
    A project item is just a blob file
    """
    implements(IProjectItem)
    __name__ = __parent__ = None

    def __init__(self, title=u'', description=u''):
        super(ProjectItem, self).__init__()
        self.title = title
        self.description = description

ProjectItemFactory = Factory(ProjectItem)

class ProjectImage(ProjectItem):
    """
    a project image
    """
    implements(IProjectImage)

ProjectImageFactory = Factory(ProjectImage)

class ProjectVideo(ProjectItem):
    """
    a project video
    """
    implements(IProjectVideo)

ProjectVideoFactory = Factory(ProjectVideo)

class ProjectItemNameChooser(NameChooser):
    """
    adapter that allows to choose the __name__ of a projectitem
    """
    adapts(IProjectContainer)
    implements(INameChooser)

    def chooseName(self, name, item):
        rawname = item.title
        newname = u''
        if name:
            newname = name
        if item is not None and len(rawname)>0:
            newname = unicode.lower(rawname).strip(' @+').replace(' ','-').replace('/','-')
        return super(ProjectItemNameChooser, self).chooseName(newname, item).encode('utf-8')

class ProjectNameChooser(ProjectItemNameChooser):
    """
    adapter that allows to choose the __name__ of a project
    """
    adapts(IProject)
    implements(INameChooser)

class SearchableTextOfProject(object):
    """
    adapter that allows to index projects
    """
    adapts(IProject)
    implements(ISearchableTextOfProject)

    def __init__(self, context):
        self.context = context

    def getSearchableText(self):
        sourcetext = texttoindex = (self.context.title or "") + " " + (self.context.description or "")
        for word in sourcetext.split():        
            for subword in [ word[i:] for i in xrange(len(word)) if len(word)>=1 ]:
                texttoindex += subword + " "
        return texttoindex

class SearchableTextOfProjectItem(SearchableTextOfProject):
    """
    adapter that allows to index project items
    """
    adapts(IProjectItem)
    implementsOnly(ISearchableTextOfProjectItem)

