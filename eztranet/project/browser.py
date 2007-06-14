# -*- coding: utf-8 -*-
from zope.interface import implements
from zope.formlib.form import EditForm, Fields, AddForm, applyChanges
from zope.publisher.browser import BrowserPage
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.traversing.browser.absoluteurl import AbsoluteURL
from zope.traversing.api import getPath
from zope.app.form import CustomWidgetFactory
from zope.app.form.browser import TextAreaWidget
from zope.app.form.browser.itemswidgets import MultiCheckBoxWidget
from zope.app.form.browser.interfaces import ITerms, ISourceQueryView
from zope.component import getAdapter, createObject, adapts, getUtility
from zope.app.container.browser.contents import Contents
from zope.app.container.interfaces import INameChooser
from zope.proxy import removeAllProxies
from zope.formlib.form import Actions, Action, getWidgetsData
from zope.copypastemove import ContainerItemRenamer
from zope.app.intid.interfaces import IIntIds
from zope.schema.vocabulary import SimpleTerm
from zope.app.file.interfaces import IImage
from zope.security.checker import canAccess, canWrite
from zope.app.renderer.plaintext import PlainTextToHTMLRenderer
import string
from zope.app.form.browser.textwidgets import escape

from interfaces import *
from project import Project, ProjectImage, ProjectVideo

class CustomTextWidget(TextAreaWidget):
    width=40
    height=5

class ProjectAdd(AddForm):
    u"""
    The view class for adding an project
    """
    form_fields=Fields(IProject).omit('__name__', '__parent__')
    form_fields['description'].custom_widget=CustomTextWidget
    label=u"New project"
    def create(self, data):
        u"on crée l'objet (ici avec le constructeur, mais on devrait utiliser une named factory)"
        self.project=Project()
        u"puis on applique les données du formulaire à l'objet (data contient les données du formulaire !)"
        applyChanges(self.project, self.form_fields, data)
        u"puis on choisit le nom de l'objet dans le container (le 1er nom dans la liste)"
        self.context.contentName=INameChooser(self.project).chooseName(self.project.title, self.project)
        return self.project

class ProjectEdit(EditForm):
    label="Edit project details"
    actions = Actions(Action('Apply', success='handle_edit_action'), )
    def __init__(self, context, request):
        self.context, self.request = context, request
        self.form_fields=Fields(IProject).omit('__name__', '__parent__')
        self.form_fields['description'].custom_widget=CustomTextWidget
        super(ProjectEdit, self).__init__(context, request)
        #template=ViewPageTemplateFile("project_form.pt")
    def handle_edit_action(self, action, data):
        super(ProjectEdit, self).handle_edit_action.success(data)
        oldname=self.context.__name__
        newname=string.lower(INameChooser(self.context).chooseName(u"",self.context))
        if string.lower(oldname)!=newname:
            renamer = ContainerItemRenamer(self.context.__parent__)
            renamer.renameItem(oldname, newname)
        return self.request.response.redirect(AbsoluteURL(self.context, self.request)()+"/edit.html")
    def validate(self, action, data):
        u"on récupère les données du formulaire et on remplit data"
        getWidgetsData(self.widgets, 'form', data)
        u"on crée un objet temporaire pour tester le nouveau nom"
        dummy=Project()
        u"on applique le formulaire au nouveau"
        applyChanges(dummy, self.form_fields, data)
        u"on calcule le nouveau nom avec le dummy (un peu loourdingue)"
        newname = INameChooser(dummy).chooseName(u"",dummy)
        u"s'il existe déjà on retourne une erreur"
        if newname in list(self.context.__parent__.keys()) and self.context != self.context.__parent__[newname]:
            return ("The name <i>"+newname+"</i> conflicts with another Project",)
        return super(ProjectEdit, self).validate(action, data)

class ProjectView(BrowserPage):
    u"la vue qui permet d'afficher un project"
    label="View of an Project"
    __call__=ViewPageTemplateFile("project.pt")
    def __init__(self, context, request):
        self.context, self.request = context, request

class ProjectContainerView(Contents):
    u"""
    la vue du container de projects.
    """
    label = u"List de vos projets"
    __call__ = ViewPageTemplateFile('projectcontainer.pt')
    def listContentInfo(self):
        u"""
        reuse the original, but remove those not permitted
        """
        info = super(ProjectContainerView, self).listContentInfo()
        return [ i for i in info if canAccess(i['object'], 'title') ]

class ProjectImageAdd(AddForm):
    u"""
    The view class for adding a ProjectImage
    """
    form_fields=Fields(IProjectItem, IFile).omit('__name__', '__parent__', 'contentType')
    form_fields['description'].custom_widget=CustomTextWidget
    label=u"nouvelle image"
    def create(self, data):
        self.image=ProjectImage()
        applyChanges(self.image, self.form_fields, data)
        if not self.image.title:
            self.image.title = self.request.form['form.data'].filename
        self.image.__parent__ = self.context.context
        self.context.contentName=INameChooser(self.context.context).chooseName(self.image.title, self.image)
        return self.image


class ProjectVideoAdd(AddForm):
    u"""
    The view class for adding a ProjectVideo
    """
    form_fields=Fields(IProjectItem, IFile).omit('__name__', '__parent__', 'contentType')
    form_fields['description'].custom_widget=CustomTextWidget
    label=u"Ajout d'une vidéo"
    def create(self, data):
        self.video=ProjectVideo()
        applyChanges(self.video, self.form_fields, data)
        if not self.video.title:
            self.video.title = self.request.form['form.data'].filename
        self.context.contentName=INameChooser(self.context.context).chooseName(self.video.title, self.video)
        return self.video

class ProjectItemEdit(EditForm):
    label="Modification"
    actions = Actions(Action('Apply', success='handle_edit_action'), )
    def __init__(self, context, request):
        self.context, self.request = context, request
        self.form_fields=Fields(IProjectItem, IFile).omit('__name__', '__parent__')
        self.form_fields['description'].custom_widget=CustomTextWidget
        super(ProjectItemEdit, self).__init__(context, request)
        #template=ViewPageTemplateFile("project_form.pt")
    def handle_edit_action(self, action, data):
        super(ProjectItemEdit, self).handle_edit_action.success(data)
        oldname=self.context.__name__
        newname=string.lower(INameChooser(self.context).chooseName(u"",self.context))
        if string.lower(oldname)!=newname:
            renamer = ContainerItemRenamer(self.context.__parent__)
            renamer.renameItem(oldname, newname)
        return self.request.response.redirect(AbsoluteURL(self.context, self.request)()+"/view.html")
    def validate(self, action, data):
        #on récupère les données du formulaire et on remplit data
        getWidgetsData(self.widgets, 'form', data)
        # on vire le champ d'upload s'il est vide pour éviter d'écraser le fichier par du vide
        #if not data['data']:
        #    self.form_fields = self.form_fields.omit('data')
        #on crée un objet temporaire pour tester le nouveau nom
        dummy=ProjectImage()
        #on applique le formulaire au nouveau
        applyChanges(dummy, self.form_fields, data)
        #on calcule le nouveau nom avec le dummy (un peu loourdingue)
        newname = INameChooser(dummy).chooseName(u"",dummy)
        #s'il existe déjà on retourne une erreur
        if newname in list(self.context.__parent__.keys()) and self.context != self.context.__parent__[newname]:
            return ("Le nom <i>"+newname+"</i> est en conflit avec un autre objet",)
        return super(ProjectItemEdit, self).validate(action, data)

class ProjectItemView(BrowserPage):
    def description(self):
        if not self.context.description:
            return None
        return PlainTextToHTMLRenderer(escape(self.context.description), self.request).render()


class ProjectImageView(ProjectItemView):
    u"la vue qui permet d'afficher un ensemble d'images"
    label="Image"
    __call__=ViewPageTemplateFile("image.pt")
    def wantedWidth(self):
        width = self.context.getImageSize()[0]
        if width > 800:
            width=800
        return width
    def originalWidth(self):
        return self.context.getImageSize()[0]

class ProjectVideoView(ProjectItemView):
    u"la vue qui permet d'afficher un ensemble d'images"
    label="Vidéo"
    __call__=ViewPageTemplateFile("video.pt")
    def getPath(self):
        return getPath(self.context)


