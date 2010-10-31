from eztranet.config.interfaces import IConfig, IConfigurable
from eztranet.importexport.interfaces import IImport, IExport
from eztranet.project.interfaces import IOrderConfig
from persistent import Persistent
from zope.app.container.btree import BTreeContainer
from zope.app.container.contained import NameChooser
from zope.app.container.interfaces import INameChooser
from zope.component import adapts
from zope.component.factory import Factory
from zope.copypastemove import ObjectCopier
from zope.event import notify
from zope.file.file import File
from zope.file.interfaces import IFile
from zope.interface import implements
from zope.lifecycleevent import ObjectCopiedEvent
from zope.security.proxy import removeSecurityProxy
from zope.size.interfaces import ISized
import PIL.Image
import os
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


class ProjectItemImport(object):
    """import plugin for an item (image or video)
    """
    implements(IImport)
    adapts(IProjectItem)
    def __init__(self, context):
        self.context = context

    def do_import(self, newfile):
        # write the file with chunks of 1MB
        if type(newfile) in (str, unicode):
            tmpfile = open(newfile)
        else:
            tmpfile = newfile
        tmpfile.seek(0)
        f = self.context.open('w')
        chunk = tmpfile.read(1000000)
        while chunk:
            f.write(chunk)
            chunk = tmpfile.read(1000000)
        del chunk
        if tmpfile is newfile:
            # don't close but rewind
            tmpfile.seek(0)
        else:
            tmpfile.close()
        f.close()


class ProjectItemExport(object):
    """export plugin for an item (image or video)
    """
    implements(IExport)
    adapts(IProjectItem)
    def __init__(self, context):
        self.context = context

    def do_export(self, filename):
        tmpfile = open(filename, 'w')
        tmpfile.write(self.read())
        tmpfile.close()



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


class ProjectTextImport(object):
    """import plugin for an item (image or video)
    """
    implements(IImport)
    adapts(IProjectText)
    def __init__(self, context):
        self.context = context

    def do_import(self, newfile):
        # write the file with chunks of 1MB
        if type(newfile) in (str, unicode):
            tmpfile = open(newfile)
        else:
            tmpfile = newfile
        tmpfile.seek(0)
        self.context.text = tmpfile.read()
        if tmpfile is newfile:
            # don't close but rewind
            tmpfile.seek(0)
        else:
            tmpfile.close()


class ProjectTextExport(object):
    """export plugin for an item (image or video)
    """
    implements(IExport)
    adapts(IProjectText)
    def __init__(self, context):
        self.context = context

    def do_export(self, filename):
        tmpfile = open(filename, 'w')
        tmpfile.write(self.text)
        tmpfile.close()


class ProjectItemNameChooser(NameChooser):
    """adapter that allows to choose the __name__ of a projectitem
    """
    adapts(IProjectContainer)
    implements(INameChooser)

    def chooseName(self, provided_name, item):
        rawname = unicode(item.title)
        newname = u''
        if provided_name:
            newname = provided_name
        if item is not None and rawname:
            newname = unicode.lower(rawname).strip(' @+').replace(' ','-').replace('/','-')
        if item is not None and not rawname and item.__name__:
            newname = item.__name__
        if newname in self.context and item is self.context[newname]:
            return newname
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
        self.context = self.__parent__ = context
        with self.context.open() as blobfile:
            image = PIL.Image.open(blobfile.name)
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


class BlobCopier(ObjectCopier):
    """Allow to copy a blob.
    The problem comes from the fact that ObjectCopier is always returned
    because the context provides IContained in the first place.
    """
    def copyTo(self, target, new_name=None):
        """Override this method to add blob copying abilities
        """
        new_name = super(BlobCopier, self).copyTo(target, new_name)
        context = removeSecurityProxy(self.context)
        if hasattr(context, '_data'):
            # create a hard link to the blob, then consume it
            with context.open() as blobfile:
                source_blob_filename = blobfile.name
            blob_copy_path = source_blob_filename+'copy'
            if os.path.exists(blob_copy_path): os.unlink(blob_copy_path)
            os.link(source_blob_filename, blob_copy_path)
            removeSecurityProxy(target[new_name])._data.consumeFile(source_blob_filename+'copy')
            # notify, so the thumbnail (or other) is created
            notify(ObjectCopiedEvent(target[new_name], context))
        return new_name

