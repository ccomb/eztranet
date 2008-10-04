from eztranet.project.interfaces import IProject, IProjectItem, IProjectText
from eztranet.project.project import Project
from eztranet.project.project import ProjectImage
from eztranet.project.project import ProjectItem
from eztranet.project.project import ProjectText
from eztranet.project.project import ProjectVideo
from eztranet.skin.interfaces import IEztranetSkin
from eztranet.thumbnail.interfaces import IThumbnail
from hachoir_parser import createParser
from os.path import basename
from z3c.contents.browser import Contents
from z3c.contents.column import RenameColumn
from z3c.form.browser.file import FileWidget
from z3c.form.converter import BaseDataConverter
from z3c.form.field import Fields
from z3c.form.form import applyChanges
from z3c.form.interfaces import IFieldWidget, IValidator
from z3c.form.validator import SimpleFieldValidator
from z3c.form.widget import FieldWidget
from z3c.formui.form import EditForm, AddForm
from z3c.menu.simple.menu import SimpleMenuItem
from z3c.pagelet.browser import BrowserPagelet
from z3c.table.column import Column
from zope.app.container.interfaces import INameChooser
from zope.component import adapts, adapter, getAdapter
from zope.copypastemove import ContainerItemRenamer
from zope.dublincore.interfaces import IDCTimes
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
from zope.interface import implements, implementer, Interface
from zope.lifecycleevent import ObjectCreatedEvent
from zope.schema.interfaces import IBytes
from zope.security.checker import canAccess
from zope.security.proxy import removeSecurityProxy
from zope.size.interfaces import ISized
from zope.traversing.api import getPath
from zope.traversing.browser.absoluteurl import absoluteURL
import zope.event
import zope.publisher
import zope.publisher.interfaces
import zope.security.interfaces
import zope.security.management

_ = MessageFactory('eztranet')


class ProjectAdd(AddForm):
    """The view class for adding a project"""

    fields=Fields(IProject).omit('__name__', '__parent__')
    label = _(u'Adding a project')
    
    def createAndAdd(self, data):
        project=Project()
        applyChanges(self, project, data)
        contentName = \
            INameChooser(self.context).chooseName(project.title,
                                                  project)
        zope.event.notify(ObjectCreatedEvent(project))
        self.context[contentName] = project
        self.request.response.redirect(absoluteURL(self.context, self.request))


class ProjectAddMenuItem(SimpleMenuItem):
    title = _(u'New folder')
    url = 'add_project.html'
    weight = 50
    

class ProjectEdit(EditForm):

    label = _(u'Project details')

    def __init__(self, context, request):
        self.context, self.request = context, request
        self.fields=Fields(IProject).omit('__name__', '__parent__')
        super(ProjectEdit, self).__init__(context, request)

    def applyChanges(self, data):
        # First do the base class edit handling
        oldname=self.context.__name__
        oldtitle = self.context.title
        super(ProjectEdit, self).applyChanges(data)
        # then rename the object in the parent container and redirect to it
        if oldtitle != self.context.title:
            newname = INameChooser(self.context.__parent__).chooseName(u"",self.context)
            renamer = ContainerItemRenamer(self.context.__parent__)
            renamer.renameItem(oldname, newname)
        self.request.response.redirect(absoluteURL(self.context, self.request))


class ProjectEditMenuItem(SimpleMenuItem):
    title = _(u'Modify')
    url = 'edit.html'
    weight = 20
    
def project_sorting(p1, p2):
    """We put projects in the beginning, and order by date, most recent first"""

    if IProject.providedBy(p1) and IProjectItem.providedBy(p2):
        return -1
    if IProject.providedBy(p2) and IProjectItem.providedBy(p1):
        return 1
    created1 = IDCTimes(p1).created
    created2 = IDCTimes(p2).created
    if created1 and created2 and created1 > created2:
        return -1
    else:
        return 1
    return 0


class ProjectView(Contents):
    """The view used to display a project"""

    startBatchingAt = 1000000

    def description(self):
        if not self.context.description:
            return None
        return self.context.description
        #return PlainTextToHTMLRenderer(escape(self.context.description), self.request).render()

    def setUpColumns(self):
        columns = super(ProjectView, self).setUpColumns()
        return [c for c in columns if type(c) is not RenameColumn]

    @property
    def values(self):
        values = [ item for item in super(ProjectView, self).values 
                   if canAccess(item, 'title') ]
        values.sort(project_sorting)
        return values


class ProjectContainerView(Contents):
    """The view for project containers"""

    allowRename = False
    description = _(u'Here is the list of your projects')
    startBatchingAt = 1000000
    def setUpColumns(self):
        columns = super(ProjectContainerView, self).setUpColumns()
        return [c for c in columns if type(c) is not RenameColumn]
    @property
    def values(self): # FIXME to have in the new z3c with permission filtering
        # turn the oobtree into a list, and filter against permissions
        values = [ item for item in super(ProjectContainerView, self).values 
                   if canAccess(item, 'title') ]
        values.sort(project_sorting)
        return values


class TitleColumn(RenameColumn):
    header = _(u'Name')
    weight = 11
    def getSortKey(self, item):
        return item.title
    def renderCell(self, item):
        return '<a href="%s">%s</a>' % (item.__name__, item.title)


class SizeColumn(Column):
    header = _(u'Size')
    weight = 120 # The 'Modified' column has a weight of 110
    def renderCell(self, item):
        return translate(ISized(item).sizeForDisplay(), context=self.request)


class ThumbnailColumn(Column):
    """column with thumbnail
    
    for z3c.contents page of object that are thumbnailed (see zcml)
    """
    header = '<a href=".."><img src="/++resource++project_img/up.png" alt="up" /></a>'
    weight = 11
    def renderCell(self, item):
        item_url = absoluteURL(item, self.request)
        thumb_url = IThumbnail(item).url
        if thumb_url is None:
            thumb_url = absoluteURL(item, self.request) + '/@@thumbnail_image'
        return '<a href="%s"><img src="%s" class="table_thumbnail" /></a>' % (item_url, thumb_url)


class ProjectContainerViewMenuItem(SimpleMenuItem):
    title = _(u'List')
    url = 'index.html'
    weight = 10


class ProjectItemAdd(AddForm):
    """The view class for adding a ProjectItem"""

    fields = Fields(IProjectItem).omit('__name__', '__parent__', 'title')
    label = _(u'Adding a file')
    id = "addform"

    def createAndAdd(self, data):
        if ('data' in data
                and type(data['data']) is zope.publisher.browser.FileUpload):
            uploaded_file = data['data']
            try: # to determine the mime_type with the hachoir
                hachoir_parser = createParser(unicode(uploaded_file.name))
                mimetype = hachoir_parser.mime_type
                data['data'].headers['Content-Type'] = mimetype
            except: # revert to what is told by the browser
                print u'**Hachoir determination failed**'
                mimetype = uploaded_file.headers['Content-Type']
            majormimetype = mimetype.split('/')[0]
            if majormimetype == 'video':
                item = ProjectVideo()
            elif majormimetype == 'image':
                item = ProjectImage()
            else :
                item = ProjectItem()
            item.title = basename(uploaded_file.filename).split('\\')[-1]
            contentName = INameChooser(self.context).chooseName(item.title,
                                                                item)
            # set some file attributes
            major, minor, parameters = zope.publisher.contenttype.parse(
                                                                     mimetype)
            if 'charset' in parameters:
                parameters['charset'] = parameters['charset'].lower()
            item.mimeType = mimetype
            item.parameters = parameters
            # write the file with chunks of 1MB
            f = item.open('w')
            uploaded_file.seek(0)
            chunk = uploaded_file.read(1000000)
            while chunk:
                f.write(chunk)
                chunk = uploaded_file.read(1000000)
            f.close()
            # add the file in the parent
            self.context[contentName] = item
            # notify the file is added
            zope.event.notify(ObjectCreatedEvent(item))
            # remove the 'data' field for the final applyChanges
            data.pop('data')
            # update all fields excepted the file fields removed in the previous loop
            applyChanges(self, item, data) # applychanges except the data
            # remove the uploaded file

        self.request.response.redirect(absoluteURL(self.context, self.request))


class BigFileWidget(FileWidget):
    adapts(IBytes, IEztranetSkin)

@adapter(IBytes, IEztranetSkin)
@implementer(IFieldWidget)
def BigFileFieldWidget(field, request):
    """IFieldWidget factory for BigFileWidget."""
    return FieldWidget(field, BigFileWidget(request))


class BigFileUploadDataConverter(BaseDataConverter):
    """A special data converter for big files

    This prevents from loading the whole uploaded file in memory"""

    adapts(IBytes, BigFileWidget)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        if value is None or value == '':
            return self.field.missing_value
    
        if isinstance(value, zope.publisher.browser.FileUpload):
            self.widget.headers = value.headers
            self.widget.filename = value.filename
            if getattr(value, 'filename', ''):
                # we return the FileUpload itself!
                return value
            else:
                return self.field.missing_value
        else:
            return unicode(value)


class BigFileValidator(SimpleFieldValidator):
    implements(IValidator)
    zope.component.adapts(
        Interface,
        Interface,
        ProjectItemAdd,
        IBytes,
        Interface)

    def validate(self, data):
        return type(data) is zope.publisher.browser.FileUpload


class ProjectItemAddMenuItem(SimpleMenuItem):
    title = _(u'New file')
    url = 'add_projectitem.html'
    weight = 50


class ProjectItemEdit(EditForm):
    label = _(u'Modification')

    def __init__(self, context, request):
        self.context, self.request = context, request
        self.fields=Fields(IProjectItem).omit('__name__', '__parent__', 'data')
        super(ProjectItemEdit, self).__init__(context, request)

    def applyChanges(self, data):
        # First do the base class edit handling
        oldname=self.context.__name__
        oldtitle = self.context.title
        super(ProjectItemEdit, self).applyChanges(data)
        # then rename the object in the parent container and redirect to it
        if oldtitle != self.context.title:
            newname = INameChooser(self.context.__parent__).chooseName(u"",self.context)
            renamer = ContainerItemRenamer(self.context.__parent__)
            renamer.renameItem(oldname, newname)
        self.request.response.redirect(absoluteURL(self.context, self.request))


class ProjectItemEditMenuItem(SimpleMenuItem):
    title = _(u'Modify')
    url = 'edit.html'
    weight = 20


class ProjectItemView(BrowserPagelet):
    """The base view for project items"""
    label = _(u'File')

    def description(self):
        if not self.context.description:
            return None
        return self.context.description
        #return PlainTextToHTMLRenderer(escape(self.context.description), self.request).render()


class ProjectItemViewMenuItem(SimpleMenuItem):
    title = _(u'View')
    url = 'index.html'
    weight = 10


class ProjectImageView(ProjectItemView):
    """The view that allows to display an image"""
    label = _(u'Image')

    def __init__(self, context, request):
        super(ProjectImageView, self).__init__(context, request)
        self.size = ISized(self.context)

    def wantedWidth(self):
        site_width = 720
        try:
            width = self.size.sizeForDisplay().split(' ')[1].split('x')[0]
        except Exception:
            width = site_width
        if width > site_width:
            width = site_width
        return width

    def originalWidth(self):
        return self.size.sizeForDisplay().split(' ')[1].split('x')[0]


class ProjectVideoView(ProjectItemView):
    """The view that allows to display a video"""
    label = _(u'Video')

    def __init__(self, context, request):
        self.context, self.request = context, request

    def getPath(self):
        return getPath(self.context)

    def callFlashView(self):
        self.context = self.context.flash_video
        return removeSecurityProxy(self.context).openDetached().read()


def _getRequest():
    #TODO : move this into a thumbnail view in eztranet.thumbnail
    i = zope.security.management.getInteraction() # raises NoInteraction

    for p in i.participations:
        if zope.publisher.interfaces.IRequest.providedBy(p):
            return p
    
    raise RuntimeError('Could not find current request.')


class ProjectThumbnail(object):
    #TODO : move this into a thumbnail view in eztranet.thumbnail?
    """adapter from a project to a thumbnail"""
    adapts(IProject)
    implements(IThumbnail)
    url = '/++resource++project_img/folder.png'

    @property
    def image(self):
        # a resource is just an adapter on the request!
        request = _getRequest()
        return getAdapter(request, name='project_img')['folder.png']

    def __init__(self, context):
        self.context = context

    def compute_thumbnail(self):
        pass


class CommentMenuItem(SimpleMenuItem):
    title = _(u'Comments')
    url = "comments.html"
    weight = 90


class FileUploadHeader(object):
    """Content provider for the js header of gp.fileupload"""

    def update(self):
        pass

    def render(self):
        submit_label = _(u'Send files...')
        link_label = _(u'Add more files...')
        return """
        <script type="text/javascript"
                src="/gp.fileupload.static/jquery.js"></script><script
                type="text/javascript"
                src="/gp.fileupload.static/jquery.fileupload.js">
        </script>
        <script type="text/javascript">
            jQuery(document).ready(function() {
                jQuery('#addform').fileUpload({
                    stat_delay: 500,
                    action:'add_projectitem.html',
                    field_name:'form.widgets.data',
                    hidden_submit_name:'form.buttons.add',
                    replace_existing_form: true,
                    submit_label:'%s',
                    link_label:'%s'});
            });
        </script>
        """ % (translate(submit_label, context=self.request),
               translate(link_label, context=self.request))



class ProjectTextAdd(AddForm):
    """The view class for adding a text file"""

    fields=Fields(IProjectText).select('title', 'text')
    label = _(u'Adding a text page')
    
    def createAndAdd(self, data):
        page = ProjectText()
        applyChanges(self, page, data)
        contentName = \
            INameChooser(self.context).chooseName(page.title,
                                                  page)
        zope.event.notify(ObjectCreatedEvent(page))
        self.context[contentName] = page
        self.request.response.redirect(absoluteURL(self.context, self.request))


class ProjectTextEdit(EditForm):
    """the view for editing a text page"""

    fields=Fields(IProjectText).select('title', 'text')
    label = _(u'Editing a text page')

    def applyChanges(self, data):
        # First do the base class edit handling
        oldname=self.context.__name__
        oldtitle = self.context.title
        super(ProjectTextEdit, self).applyChanges(data)
        # then rename the object in the parent container and redirect to it
        if oldtitle != self.context.title:
            newname = INameChooser(self.context.__parent__).chooseName(u"",self.context)
            renamer = ContainerItemRenamer(self.context.__parent__)
            renamer.renameItem(oldname, newname)
        self.request.response.redirect(absoluteURL(self.context, self.request))


class ProjectTextView(BrowserPagelet):
    """view that allows to display a text page"""
    label = _(u'Text page')

    def text(self):
        if not self.context.text:
            return None
        return self.context.text
        #return PlainTextToHTMLRenderer(escape(self.context.text), self.request).render()

class ProjectTextAddMenuItem(SimpleMenuItem):
    title = _(u'New text')
    url = 'add_page.html'
    weight = 60


