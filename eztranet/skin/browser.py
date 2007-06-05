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
    """
    implements(IContentProvider)
    adapts(Interface, IDefaultBrowserLayer, Interface)
    def __init__(self, context, request, view):
        self.context, self.request, self.view = context, request, view
        self._sitename = getSite().__name__
    def update(self):
        u"on récupère le nom du contexte s'il en a un"
        if hasattr(self.context,'__name__') and self.context.__name__ is not None:
            self._pagetitle = self.context.__name__ + " - " + self._sitename
        else:
            self._pagetitle = self._sitename
    def render(self):
        return self._pagetitle

class LogoProvider(object):
    u"""
    The view that provides the logo and accessories
    """
    implements(IContentProvider)
    adapts(Interface, IDefaultBrowserLayer, Interface)
    def __init__(self, context, request, view):
        self.context, self.request, self.view = context, request, view
    def __call__(self):
        return self
    def update(self):
        try:
            self.logo = getSite()['logo']
        except:
            self.logo = None
        self.title = getSite().__name__
        self.url = AbsoluteURL(self.logo, self.request)()
    def render(self):
        u"Instead of rendering HTML, we return a dict with what we want to be traversed in TALES"
        return { 'url':self.url, 'title': self.title, 'alt':self.title }

