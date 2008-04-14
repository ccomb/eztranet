from zope.interface import alsoProvides
from zope.formlib.form import EditForm, Fields, AddForm, applyChanges
from zope.publisher.browser import BrowserPage
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.traversing.browser.absoluteurl import AbsoluteURL
from zope.traversing.api import getPath
from zope.app.form.browser import TextAreaWidget
from zope.app.container.browser.contents import Contents
from zope.app.container.interfaces import INameChooser
from zope.formlib.form import Actions, Action, getWidgetsData
from zope.copypastemove import ContainerItemRenamer
from zope.security.checker import canAccess
from zope.app.renderer.plaintext import PlainTextToHTMLRenderer
from zope.app.form.browser.textwidgets import escape
from zope.app.file.browser.image import ImageData
from zope.app.file.browser.file import FileView
from zope.app.file import File
from zope.dublincore.interfaces import IDCTimes
from zope.contenttype import guess_content_type
from zope.security.proxy import removeSecurityProxy
import zope.file

from eztranet.project.interfaces import IProject, IProjectItem, IProjectImage, IProjectVideo
from eztranet.project.project import Project, ProjectItem
        
class CustomTextWidget(TextAreaWidget):
    width=40
    height=5

class ProjectAdd(AddForm):
    u"""
    The view class for adding an project
    """
    form_fields=Fields(IProject).omit('__name__', '__parent__')
    form_fields['description'].custom_widget=CustomTextWidget
    label=u"Ajout d'un projet"
    def create(self, data):
        self.project=Project()
        applyChanges(self.project, self.form_fields, data)
        self.context.contentName=INameChooser(self.context.context).chooseName(self.project.title, self.project)
        return self.project

class ProjectEdit(EditForm):
    label="Modification du projete"
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
        return self.request.response.redirect(AbsoluteURL(self.context, self.request)()+"/view.html")

def project_sorting(p1, p2):
    u"We put projects in the beginning, and order by date, most recent first"
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
    u"la vue qui permet d'afficher un project"
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
    u"""
    la vue du container de projects.
    """
    label = u"Projets"
    __call__ = ViewPageTemplateFile('project.pt')
    description = u"Voici la liste de vos différents projets"
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

class ProjectItemAdd(zope.file.upload.Upload):
    u"""
    The view class for adding a ProjectItem
    """
    form_fields=Fields(IProjectItem).omit('__name__', 'title', '__parent__', 'contentType')
    form_fields['description'].custom_widget=CustomTextWidget
    label=u"Ajout d'un fichier"
    extra_script = u"""
    document.open()
    document.write("<p id='loading' style='display: none'><img src='/@@/loading.gif' alt='loading' style='float: left\; margin-right: 10px\;' />Le fichier est en cours d'envoi, cela peut prendre plusieurs minutes...<br/>Si vous interrompez le chargement de cette page, l'opération sera annulée.</p>")
    document.close()
    document.getElementById('form.actions.add').onclick= function() { document.getElementById('loading').style.display='block'; }
    """
    def add(self, obj):
        majormimetype = obj.mimeType.split('/')[0]
        if majormimetype == 'video':
            alsoProvides(obj, IProjectVideo)
        elif majormimetype == 'image':
            alsoProvides(obj, IProjectImage)
        super(ProjectItemAdd, self).add(obj)

    def _create_instance(self, data):
        return ProjectItem()


class ProjectItemEdit(EditForm):
    label="Modification"
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
        return self.request.response.redirect(AbsoluteURL(self.context, self.request)()+"/view.html")

class ProjectItemView(BrowserPage):
    def description(self):
        if not self.context.description:
            return None
        return PlainTextToHTMLRenderer(escape(self.context.description), self.request).render()

class ProjectImageView(ProjectItemView):
    u"la vue qui permet d'afficher une image"
    label=u"Image"
    __call__=ViewPageTemplateFile("image.pt")

    def wantedWidth(self):
        width = self.context.getImageSize()[0]
        if width > 720:
            width=720
        return width

    def originalWidth(self):
        return self.context.getImageSize()[0]

