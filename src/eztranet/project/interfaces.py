from zope.app.container.interfaces import IContainer, IContained
from zope.app.container.constraints import contains, containers
from zope.schema import TextLine, Text, Bytes
from zope.index.text.interfaces import ISearchableText
from zope.interface import Interface, Attribute
from zope.file.interfaces import IFile
from zope.app.file.interfaces import IImage

class IProject(IContainer, IContained):
    """
    a project that will contain items or subprojects.
    This interface is added on regular zope folders.
    """
    containers("eztranet.project.interfaces.IProjectContainer",
               "eztranet.project.interfaces.IProject")
    contains("eztranet.project.interfaces.IProject",
             "eztranet.project.interfaces.IProjectItem")
    title = TextLine(title=u'titre',
                     description=u'Project title')
    description = Text(title=u"Description",
                       description=u'Project description',
                       required=False,
                       max_length=1000)

class IProjectItem(Interface):
    """
    a project item (image or video)
    This interface is only used to describe data of interest
    in an uploaded file, and to generate the adding and edit forms.
    """
    containers("eztranet.project.interfaces.IProject")
    data = Bytes(title = u'File',
                 description = u'File you want to upload')
    title = TextLine(title=u'File name',
                     description=u'Name of the uploaded file',
                     required=False)
    description = Text(title=u'Description',
                       description=u'File description',
                       required=False,
                       max_length=1000)

class IProjectVideo(IProjectItem):
    """
    a marker interface to distinguish a video
    """

class IProjectImage(IProjectItem):
    """
    a marker interface to distinguish an image
    """

class IProjectContainer(IContainer, IContained):
    """
    a toplevel container for the projects should only contain projects or items
    """
    contains(IProject)
    title=TextLine(title=u'Title',
                   description=u'Title of the project container')

class ISearchableTextOfProject(ISearchableText):
    """
    We declare an index just for this interface, so that
    only project are indexed
    """
    
class ISearchableTextOfProjectItem(ISearchableText):
    """
    We declare an index just for this interface, so that
    only projectitems are indexed
    """
