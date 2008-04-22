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
from eztranet.thumbnail.interfaces import IThumbnail
from zope.component import adapts
from zope.interface import implements
        
class CustomTextWidget(TextAreaWidget):
    width=40
    height=5

class ProjectAdd(AddForm):
    """
    The view class for adding an project
    """
    form_fields=Fields(IProject).omit('__name__', '__parent__')
    form_fields['description'].custom_widget=CustomTextWidget
    label = u"Adding a project"
    def create(self, data):
        self.project=Project()
        applyChanges(self.project, self.form_fields, data)
        self.context.contentName = \
            INameChooser(self.context.context).chooseName(self.project.title,
                                                          self.project)
        return self.project

class ProjectEdit(EditForm):
    label = u'Modification of the project'
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
        return self.request.response.redirect(AbsoluteURL(self.context, self.request)())

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
    label=u"Vue d'un projet"
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
    label = u"Projects"
    __call__ = ViewPageTemplateFile('project.pt')
    description = u"Here is the list of your projects"
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
    form_fields=Fields(IProjectItem).omit('__name__', 'title', '__parent__', 'contentType')
    form_fields['description'].custom_widget=CustomTextWidget
    label=u"Adding a file"
    extra_script = u"""
    document.open()
    document.write("<p id='loading' style='display: none'><img src='/@@/loading.gif' alt='loading' style='float: left\; margin-right: 10px\;' />The file is being uploaded, this can take several minutes...<br/>If you stop the loading of this page, the transfer will be canceled.</p>")
    document.close()
    document.getElementById('form.actions.add').onclick= function() { document.getElementById('loading').style.display='block'; }
    """

    def _create_instance(self, data):
        majormimetype = self.request.form['form.data'].headers['Content-Type'].split('/')[0]
        if majormimetype == 'video':
            return ProjectVideo()
        elif majormimetype == 'image':
            return ProjectImage()
        else :
            return ProjectItem()

class ProjectItemEdit(EditForm):
    label = u'Modification'
    actions = Actions(Action('Apply', success='handle_edit_action'), )

    def __init__(self, context, request):
        self.context, self.request = context, request
        self.form_fields=Fields(IProjectItem).omit('__name__', '__parent__')
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
    label = u'File'
    __call__ = ViewPageTemplateFile("file.pt")

    def description(self):
        if not self.context.description:
            return None
        return PlainTextToHTMLRenderer(escape(self.context.description), self.request).render()

class ProjectImageView(ProjectItemView):
    """
    The view that allows to display an image
    """
    label = u'Image'
    __call__=ViewPageTemplateFile("image.pt")

    def wantedWidth(self):
        width = self.context.getImageSize()[0]
        if width > 720:
            width=720
        return width

    def originalWidth(self):
        return self.context.getImageSize()[0]

class ProjectVideoView(ProjectItemView):
    """
    The view that allows to display a video
    """
    label = u'Video'
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
