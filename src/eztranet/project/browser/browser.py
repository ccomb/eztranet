from eztranet.project.interfaces import IProject, IProjectItem
from eztranet.project.project import Project
from eztranet.project.project import ProjectImage
from eztranet.project.project import ProjectItem
from eztranet.project.project import ProjectVideo
from eztranet.thumbnail.interfaces import IThumbnail
from hachoir_parser import createParser
from os.path import basename
from z3c.contents.browser import Contents
from z3c.contents.column import RenameColumn
from z3c.form.action import Actions, Action
from z3c.form.field import Fields
from z3c.form.form import applyChanges
from z3c.formui.form import EditForm, AddForm
from z3c.menu.simple.menu import SimpleMenuItem
from z3c.pagelet.browser import BrowserPagelet
from z3c.table.column import Column
from zope.app.container.interfaces import INameChooser
from zope.app.form.browser import TextAreaWidget
from zope.app.form.browser.textwidgets import escape
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.renderer.plaintext import PlainTextToHTMLRenderer
from zope.component import adapts
from zope.copypastemove import ContainerItemRenamer
from zope.dublincore.interfaces import IDCTimes
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
from zope.interface import implements
from zope.lifecycleevent import ObjectCreatedEvent
from zope.security.checker import canAccess
from zope.security.proxy import removeSecurityProxy
from zope.size.interfaces import ISized
from zope.traversing.api import getPath
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.viewlet.manager import ViewletManager

import zope.event
import zope.publisher

_ = MessageFactory('eztranet')

class CustomTextWidget(TextAreaWidget):
    width=40
    height=5

class ProjectAdd(AddForm):
    """
    The view class for adding an project
    """
    fields=Fields(IProject).omit('__name__', '__parent__')
    fields['description'].custom_widget=CustomTextWidget
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
    #actions = Actions(Action('Apply', success='handle_edit_action'), )
    def __init__(self, context, request):
        self.context, self.request = context, request
        self.fields=Fields(IProject).omit('__name__', '__parent__')
        self.fields['description'].custom_widget=CustomTextWidget
        super(ProjectEdit, self).__init__(context, request)
    def handle_edit_action(self, action, data):
        # First do the base class edit handling
        super(ProjectEdit, self).handle_edit_action.success(data)
        # then rename the object in the parent container and redirect to it
        oldname=self.context.__name__
        newname=INameChooser(self.context.__parent__).chooseName(u"",self.context)
        #INameChooser(self.context.__parent__).checkName(newname,self.context)
        if oldname!=newname:
            renamer = ContainerItemRenamer(self.context.__parent__)
            renamer.renameItem(oldname, newname)
        self.request.response.redirect(absoluteURL(self.context, self.request))

class ProjectEditMenuItem(SimpleMenuItem):
    title = _(u'Modify')
    url = 'edit.html'
    weight = 50
    
def project_sorting(p1, p2):
    """
    We put projects in the beginning, and order by date, most recent first
    """
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
    """
    The view used to display a project
    """
    startBatchingAt = 1000000
    def description(self):
        if not self.context.description:
            return None
        return PlainTextToHTMLRenderer(escape(self.context.description), self.request).render()

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
    """
    The view for project containers
    """
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
    """
    column with thumbnail for z3c.contents page of
    object that are thumbnailed (see zcml)
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
    """
    The view class for adding a ProjectItem
    """
    fields = Fields(IProjectItem).omit('__name__', '__parent__', 'title')
    #fields['description'].custom_widget = CustomTextWidget
    label = _(u'Adding a file')
    id = "addform"

    def update(self):
        return super(ProjectItemAdd, self).update()

    def createAndAdd(self, data):
        # We parse the form, looking for file fields
        at_least_one_file = False
        for num,fieldname in enumerate(self.request.form):
            uploaded_file = self.request.form[fieldname]
            if type(uploaded_file) is not zope.publisher.browser.FileUpload:
                continue
            try: # to determine the mime_type with the hachoir
                hachoir_parser = createParser(unicode(uploaded_file.name))
                mimetype = hachoir_parser.mime_type
                self.request.form[fieldname].headers['Content-Type'] = mimetype
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
            at_least_one_file = True
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
            # remove the file field for the final applyChanges
            self.fields = self.fields.omit(fieldname)
            
            # update all fields excepted the file fields removed in the previous loop
            applyChanges(self, item, data) # applychanges except the data

        if not at_least_one_file:
            return
        self.request.response.redirect(absoluteURL(self.context, self.request))

class ProjectItemAddMenuItem(SimpleMenuItem):
    title = _(u'New file')
    url = 'add_projectitem.html'
    weight = 50

class ProjectItemEdit(EditForm):
    label = _(u'Modification')
    #actions = Actions(Action('Apply', success='handle_edit_action'), )

    def __init__(self, context, request):
        self.context, self.request = context, request
        self.fields=Fields(IProjectItem).omit('__name__', '__parent__', 'data')
        self.fields['description'].custom_widget=CustomTextWidget
        super(ProjectItemEdit, self).__init__(context, request)

    def handle_edit_action(self, action, data):
        # First do the base class edit handling
        super(ProjectItemEdit, self).handle_edit_action.success(data)
        # then rename the object in the parent container and redirect to it
        oldname=self.context.__name__
        newname=INameChooser(self.context.__parent__).chooseName(u"",self.context)
        if oldname!=newname:
            INameChooser(self.context.__parent__).checkName(newname,self.context)
            renamer = ContainerItemRenamer(self.context.__parent__)
            renamer.renameItem(oldname, newname)
        return self.request.response.redirect(absoluteURL(self.context, self.request))

class ProjectItemEditMenuItem(SimpleMenuItem):
    title = _(u'Modify')
    url = 'edit.html'
    weight = 50

class ProjectItemView(BrowserPagelet):
    """
    The base view for project items
    """
    label = _(u'File')

    def description(self):
        if not self.context.description:
            return None
        return PlainTextToHTMLRenderer(escape(self.context.description), self.request).render()

class ProjectItemViewMenuItem(SimpleMenuItem):
    title = _(u'View')
    url = 'index.html'
    weight = 10

class ProjectImageView(ProjectItemView):
    """
    The view that allows to display an image
    """
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
    """
    The view that allows to display a video
    """
    label = _(u'Video')

    def __init__(self, context, request):
        self.context, self.request = context, request

    def getPath(self):
        return getPath(self.context)

    def callFlashView(self):
        self.context = self.context.flash_video
        return removeSecurityProxy(self.context).openDetached().read()

class ProjectThumbnail(object):
    """
    adapter from a project to a thumbnail
    """
    adapts(IProject)
    implements(IThumbnail)
    image = None
    url = '/++resource++project_img/folder.png'

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


