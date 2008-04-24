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
from zope.size.interfaces import ISized
import PIL.Image
import os
from interfaces import IProjectContainer, IProjectItem, IProject, \
                       IProjectImage, IProjectVideo
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
    __name__ = __parent__ = data = None

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
        return super(ProjectItemNameChooser, self).chooseName(newname, item)

class ProjectNameChooser(ProjectItemNameChooser):
    """
    adapter that allows to choose the __name__ of a project
    """
    adapts(IProject)
    implements(INameChooser)

class ProjectImageSized(object):
    """
    adapter to ISized for an image
    """
    adapts(IProjectImage)
    implements(ISized)

    def __init__(self, context):
        self.context = context
        image = PIL.Image.open(self.context._data._current_filename())
        self.width = image.size[0]
        self.height = image.size[1]
        self.size = self.context.size

    def sizeForDisplay(self):
        """
        returns a size of the form '3125KB 640x480'
        """
        image = PIL.Image.open(self.context._data._current_filename())
        return '%sKB %sx%s' % (self.size/1024, self.width, self.height)

    def sizeForSorting(self):
        return ('KB', self.size)




