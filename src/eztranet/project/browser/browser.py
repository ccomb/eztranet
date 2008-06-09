from zope.formlib.form import EditForm, Fields, AddForm, applyChanges
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.traversing.browser.absoluteurl import AbsoluteURL
from zope.traversing.api import getPath
from zope.app.form.browser import TextAreaWidget
from zope.app.container.browser.contents import Contents
from zope.app.container.interfaces import INameChooser
from zope.formlib.form import Actions, Action
from zope.copypastemove import ContainerItemRenamer
from zope.security.checker import canAccess
from zope.app.renderer.plaintext import PlainTextToHTMLRenderer
from zope.app.form.browser.textwidgets import escape
from zope.dublincore.interfaces import IDCTimes
from zope.security.proxy import removeSecurityProxy
from zope.file.upload import Upload
from zope.file.download import Download
from eztranet.project.interfaces import IProject, IProjectItem
from eztranet.project.project import Project, ProjectItem, \
                                     ProjectImage, ProjectVideo
from zope.size.interfaces import ISized
import zope.event
from zope.lifecycleevent import ObjectCreatedEvent
from eztranet.thumbnail.interfaces import IThumbnail
from zope.component import adapts
from zope.interface import implements
from os.path import basename
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('eztranet')
from hachoir_parser import createParser
from os.path import join
from eztranet.project.browser.multiupload.browser import MultiUploadWidget
import zope.publisher

class CustomTextWidget(TextAreaWidget):
    width=40
    height=5


class ProjectAdd(AddForm):
    """
    The view class for adding an project
    """
    form_fields=Fields(IProject).omit('__name__', '__parent__')
    form_fields['description'].custom_widget=CustomTextWidget
    label = _(u'Adding a project')
    
    def createAndAdd(self, data):
        project=Project()
        applyChanges(project, self.form_fields, data)
        contentName = \
            INameChooser(self.context).chooseName(project.title,
                                                  project)
        zope.event.notify(ObjectCreatedEvent(project))
        self.context[contentName] = project
        self.request.response.redirect(AbsoluteURL(self.context, self.request)())

class ProjectEdit(EditForm):
    label = _(u'Project details')
    actions = Actions(Action('Apply', success='handle_edit_action'), )
    def __init__(self, context, request):
        self.context, self.request = context, request
        self.form_fields=Fields(IProject).omit('__name__', '__parent__')
        self.form_fields['description'].custom_widget=CustomTextWidget
        super(ProjectEdit, self).__init__(context, request)
        #template=ViewPageTemplateFile("project_form.pt")
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
        self.request.response.redirect(AbsoluteURL(self.context, self.request)())

def project_sorting(p1, p2):
    """
    We put projects in the beginning, and order by date, most recent first
    """
    if IProject.providedBy(p1['object']) and IProjectItem.providedBy(p2['object']):
        return -1
    if IProject.providedBy(p2['object']) and IProjectItem.providedBy(p1['object']):
        return 1
    if IDCTimes(p1['object']).created > IDCTimes(p2['object']).created:
        return -1
    else:
        return 1
    return 0


class ProjectView(Contents):
    """
    The view used to display a project
    """
    label=_(u'View of a project')
    __call__=ViewPageTemplateFile("project.pt")
    def __init__(self, context, request):
        self.context, self.request = context, request
    def description(self):
        if not self.context.description:
            return None
        return PlainTextToHTMLRenderer(escape(self.context.description), self.request).render()
    def listContentInfo(self):
        contentinfo = super(ProjectView, self).listContentInfo()
        try:
            contentinfo.sort(project_sorting)
        except:
            pass
        return contentinfo

class ProjectContainerView(Contents):
    """
    The view for project containers
    """
    label = _(u'Projects')
    __call__ = ViewPageTemplateFile('project.pt')
    description = _(u'Here is the list of your projects')
    def listContentInfo(self):
        u"""
        reuse the original, but remove those not permitted
        """
        info = super(ProjectContainerView, self).listContentInfo()
        ret = [ i for i in info if canAccess(i['object'], 'title') ]
        try:
            ret.sort(project_sorting)
        except:
            pass
        return ret

class ProjectItemAdd(Upload):
    """
    The view class for adding a ProjectItem
    """
    template = ViewPageTemplateFile('add_projectitem.pt')
    form_fields = Fields(IProjectItem).omit('__name__', '__parent__', 'title')
    form_fields['description'].custom_widget = CustomTextWidget
    form_fields['data'].custom_widget = MultiUploadWidget
    label = _(u'Adding a file')
    extra_script = _(u"""
        document.open()
        document.write("<p id='loading' style='display: none'><img src='/@@/loading.gif' alt='loading' style='float: left\; margin-right: 10px\;' /> %s</p>")
        document.close()
        document.getElementById('form.actions.add').onclick = function() { document.getElementById('loading').style.display='block'; }
    """ % u'The file is being uploaded, this can take several minutes...<br/>\
              If you stop the loading of this page, the transfer will be canceled.')

    def createAndAdd(self, data):
        #data['data'] is empty because the main file field is empty
        # however we get the uploaded file ready for use
        i = 0
        for num,index in enumerate(self.request.form):
            if index != 'form.data' and not index.startswith('defaults_'):
                i += 1
                continue
            uploaded_file = self.request.form[index]
            if type(uploaded_file) != zope.publisher.browser.FileUpload:
                i+=1
                continue
            try:
                # determine the mime_type with the hachoir
                hachoir_parser = createParser(unicode(uploaded_file.name))
                mimetype = hachoir_parser.mime_type
                self.request.form[index].headers['Content-Type'] = mimetype
            except:
                # revert to what is told by the browser
                mimetype = uploaded_file.headers['Content-Type']
            majormimetype = mimetype.split('/')[0]
            if majormimetype == 'video':
                item = ProjectVideo()
            elif majormimetype == 'image':
                item = ProjectImage()
            else :
                item = ProjectItem()

            item.title = basename(uploaded_file.filename).split('\\')[-1]
            applyChanges(item, self.form_fields.omit('data'), data)
            contentName = INameChooser(self.context).chooseName(item.title,
                                                                item)
            major, minor, parameters = zope.publisher.contenttype.parse(
                                                            mimetype)
            if "charset" in parameters:
                parameters["charset"] = parameters["charset"].lower()
            item.mimeType = mimetype
            item.parameters = parameters
            f = item.open('w')
            uploaded_file.seek(0)
            chunk = uploaded_file.read(1000000)
            while chunk:
                f.write(chunk)
                chunk = uploaded_file.read(1000000)
            f.close()

            self.context[contentName] = item
            zope.event.notify(ObjectCreatedEvent(item))
            i += 1

        self.request.response.redirect(AbsoluteURL(self.context,
                                                   self.request)())

class ProjectItemEdit(EditForm):
    label = _(u'Modification')
    actions = Actions(Action('Apply', success='handle_edit_action'), )

    def __init__(self, context, request):
        self.context, self.request = context, request
        self.form_fields=Fields(IProjectItem).omit('__name__', '__parent__', 'data')
        self.form_fields['description'].custom_widget=CustomTextWidget
        super(ProjectItemEdit, self).__init__(context, request)
        #template=ViewPageTemplateFile("project_form.pt")

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
        return self.request.response.redirect(AbsoluteURL(self.context, self.request)())

class ProjectItemView(Download):
    """
    The base view for project items
    """
    label = _(u'File')
    __call__ = ViewPageTemplateFile("file.pt")

    def description(self):
        if not self.context.description:
            return None
        return PlainTextToHTMLRenderer(escape(self.context.description), self.request).render()

class ProjectImageView(ProjectItemView):
    """
    The view that allows to display an image
    """
    label = _(u'Image')
    __call__=ViewPageTemplateFile("image.pt")

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
    __call__=ViewPageTemplateFile("video.pt")

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
    url = '/@@/folder.png'

    def __init__(self, context):
        self.context = context

    def compute_thumbnail(self):
        pass
