from eztranet.config.interfaces import IConfigForm
from eztranet.tinymce import HtmlText
from zope.app.container.constraints import contains, containers
from zope.app.container.interfaces import IContainer, IContained
from zope.file.interfaces import IFile
from zope.i18nmessageid import MessageFactory
from zope.index.text.interfaces import ISearchableText
from zope.interface import Interface, implements
from zope.schema import TextLine, Bytes, Int
from zope.schema.interfaces import IBytes, IField

_ = MessageFactory('eztranet')


class IProject(IContainer, IContained):
    """a project that will contain items or subprojects.

    This interface is added on regular zope folders.
    """
    containers("eztranet.project.interfaces.IProjectContainer",
               "eztranet.project.interfaces.IProject")
    contains("eztranet.project.interfaces.IProject",
             "eztranet.project.interfaces.IProjectItem",
             "eztranet.project.interfaces.IProjectText")
    title = TextLine(title=_(u'title'),
                     description=_(u'Project title'))
    description = HtmlText(title=_(u'Description'),
                       description=_(u'Project description'),
                       required=False,
                       max_length=1000)

class ILargeBytes(IField):
    """schema field interface for a large file"""

class LargeBytes(Bytes):
    """schema field for a large file"""
    implements(ILargeBytes)

    def _validate(self, value):
        super(LargeBytes, self)._validate(value)


class IProjectItem(Interface):
    """a project item (image or video)

    This interface is only used to describe data of interest
    in an uploaded file, and to generate the adding and edit forms.
    """

    #containers("eztranet.project.interfaces.IProject")
    data = LargeBytes(title=_(u'File'),
                 description=_(u'The file you want to upload'),
                 required=False)
    title = TextLine(title=_(u'File name'),
                     description=_(u'Name of the uploaded file'),
                     required=False)
    description = HtmlText(title=_(u'Description'),
                       description=_(u'File description'),
                       required=False,
                       max_length=1000)


class IProjectVideo(IProjectItem, IFile):
    """a marker interface to distinguish a video"""


class IProjectImage(IProjectItem, IFile):
    """a marker interface to distinguish an image"""

class IProjectText(IProjectItem):
    """a marker interface to distinguish a text page"""

    text = HtmlText(title=_(u'page content')
)

class IProjectContainer(IContainer, IContained):
    """a toplevel container for the projects
    
    It should only contain projects or items"""

    contains(IProject, IProjectText)
    title=TextLine(title=_(u'Title'),
                   description=_(u'Title of the project container'))


class ISearchableTextOfProject(ISearchableText):
     """we declare an index just for this interface to index just projects"""


class ISearchableTextOfProjectItem(ISearchableText):
     """we declare an index just for this interface to index just items"""

class IOrderConfig(IConfigForm):
    """Interface of the configuration form for ordering"""

    order = Int(title = _(u'Order'),
                description = _(u'A number allowing to order the items'),
                required = False,
                default = None)
