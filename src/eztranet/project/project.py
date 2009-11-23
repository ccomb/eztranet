from persistent import Persistent
from eztranet.project.interfaces import IOrderConfig
from eztranet.config.interfaces import IConfigurable
from eztranet.config.interfaces import IConfig
from zope.app.container.btree import BTreeContainer
from zope.app.container.contained import NameChooser
from zope.app.container.interfaces import INameChooser
from zope.component import adapts
from zope.component.factory import Factory
from zope.file.file import File
from zope.interface import implements
from zope.size.interfaces import ISized
import PIL.Image
from interfaces import IProjectContainer, IProjectItem, IProject, \
                       IProjectImage, IProjectVideo, IProjectText
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('eztranet')


class ProjectContainer(BTreeContainer):
    """a project container
    """
    implements(IProjectContainer)
    __name__ = __parent__ = None


ProjectContainerFactory = Factory(ProjectContainer)


class Project(BTreeContainer):
    """a project (also a container for sub-projects)
    """
    implements(IProject)
    __name__ = __parent__ = None

    def __init__(self, title=u'', description=u''):
        super(Project, self).__init__( )
        self.title = title
        self.description = description


ProjectFactory = Factory(Project)


class ProjectItem(File):
    """A project item is just a blob file
    """
    implements(IProjectItem)
    __name__ = __parent__ = data = None

    def __init__(self, title=u'', description=u''):
        super(ProjectItem, self).__init__()
        self.title = title
        self.description = description


ProjectItemFactory = Factory(ProjectItem)


class ProjectImage(ProjectItem):
    """a project image
    """
    implements(IProjectImage)


ProjectImageFactory = Factory(ProjectImage)


class ProjectVideo(ProjectItem):
    """a project video"""

    implements(IProjectVideo)


ProjectVideoFactory = Factory(ProjectVideo)


class ProjectText(Persistent):
    """a project text page
    """
    text = description = title = data = None
    implements(IProjectText)


ProjectTextFactory = Factory(ProjectText)


class ProjectItemNameChooser(NameChooser):
    """adapter that allows to choose the __name__ of a projectitem
    """
    adapts(IProjectContainer)
    implements(INameChooser)

    def chooseName(self, provided_name, item):
        rawname = item.title
        newname = u''
        if provided_name:
            newname = provided_name
        if item is not None and rawname:
            newname = unicode.lower(rawname).strip(' @+').replace(' ','-').replace('/','-')
        if item is not None and not rawname and item.__name__:
            newname = item.__name__
        return super(ProjectItemNameChooser, self).chooseName(newname, item)


class ProjectNameChooser(ProjectItemNameChooser):
    """adapter that allows to choose the __name__ of a project
    """
    adapts(IProject)
    implements(INameChooser)


class ProjectImageSized(object):
    """adapter to ISized for an image
    """
    adapts(IProjectImage)
    implements(ISized)

    def __init__(self, context):
        self.context = context
        image = PIL.Image.open(self.context._data._current_filename())
        self.width = image.size[0]
        self.height = image.size[1]
        self.size = self.context.size
        image.fp.close()

    def sizeForDisplay(self):
        """returns a size of the form '3125KB 640x480'
        """
        return _(u'%sKB %sx%s') % (self.size/1024, self.width, self.height)

    def sizeForSorting(self):
        return (_(u'KB'), self.size)


ORDER_CONFIG_KEY = 'eztranet.project.order'

class OrderConfig(object):
    """adapter for the order form
    """
    implements(IOrderConfig)
    adapts(IConfigurable)

    def __init__(self, context):
        self.context = context

    def _get_order(self):
        return IConfig(self.context).get_config(ORDER_CONFIG_KEY)

    def _set_order(self, order):
        IConfig(self.context).set_config(ORDER_CONFIG_KEY, order)

    order = property(_get_order, _set_order)

