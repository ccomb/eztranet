# -*- coding: utf-8 -*-
from zope.app.container.interfaces import IContainer, IContained
from zope.app.container.constraints import contains, containers
from zope.schema import List, TextLine, URI, Text, Choice, List
from zope.index.text.interfaces import ISearchableText
from zope.interface import Attribute, Interface
from zope.interface.interfaces import IInterface
from zope.app.file.interfaces import IFile, IImage
from zope.app.folder.interfaces import IFolder

class IProject(IContainer, IContained):
    u"""
    a project that will contain items or subprojects.
    """
    containers("eztranet.project.interfaces.IProjectContainer", "eztranet.project.interfaces.IProject")
    contains("eztranet.project.interfaces.IProject", "eztranet.project.interfaces.IProjectItem")
    title=TextLine(title=u'titre', description=u'Titre du projet')
    description = Text(title=u"description", description=u"Description du projet", required=False, max_length=1000)


class IProjectItem(IContained):
    u"""
    a project item (image or video)
    """
    containers("eztranet.project.interfaces.IProject")
    title = TextLine(title=u'nom de fichier', description=u'Nom du fichier', required=False)
    description = Text(title=u"description", description=u"Description du fichier", required=False, max_length=1000)

class IProjectImage(IProjectItem, IImage):
    u"marker interface to tell this is a project image"

class IProjectVideo(IProjectItem, IFile):
    u"marker interface for project video"
    flash_video = Attribute("The video converted to flash")
    flash_video_tempfile = Attribute("Path of the target compressed file, or status of the compression")

class IProjectContainer(IContainer, IContained):
    u"""
    a toplevel container for the projects should only contain projects or items
    """
    contains(IProject)

class ISearchableTextOfProject(ISearchableText):
    u"""
    on déclare un index juste pour cette interface de façon à indexer juste les projets
    """
    
class ISearchableTextOfProjectItem(ISearchableText):
    u"""
    on déclare un index juste pour cette interface de façon à indexer juste les articles
    """
