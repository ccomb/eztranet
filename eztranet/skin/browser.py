# -*- coding: utf-8 -*-
from zope.traversing.browser.absoluteurl import SiteAbsoluteURL, AbsoluteURL
from zope.viewlet.manager import ViewletManagerBase
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import implements, Interface
from zope.component import adapts
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.app.component.hooks import getSite
from zope.component import createObject
from zope.publisher.browser import BrowserView

from interfaces import *

class PageTitleContentProvider(object):
    u"""
    Un Content Provider qui permet d'afficher le titre de la page (dans le header html)
    C'est important car ça aide le référencement
    """
    implements(IContentProvider)
    adapts(Interface, IDefaultBrowserLayer, Interface)
    def __init__(self, context, request, view):
        self.context=context
        self._sitename = getSite().__name__

    def update(self):
        u"on récupère le nom du contexte s'il en a un"
        if hasattr(self.context,'__name__') and self.context.__name__ is not None:
            self._pagetitle = self.context.__name__ + " - " + self._sitename
        else:
            self._pagetitle = self._sitename
    def render(self):
        return self._pagetitle