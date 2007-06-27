# -*- coding: utf-8 -*-
from zope.traversing.browser.absoluteurl import SiteAbsoluteURL, AbsoluteURL
from zope.viewlet.manager import ViewletManagerBase
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import implements, Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.app.component.hooks import getSite
from zope.component import createObject, getUtility, adapts, queryUtility
from zope.publisher.browser import BrowserView
from zope.app.publisher.interfaces.browser import IBrowserMenu
from zope.app.publisher.browser.menu import BrowserMenu
from zope.app.securitypolicy.interfaces import IPrincipalRoleManager
from zope.security.checker import canAccess
from zope.app.authentication.interfaces import IAuthenticatorPlugin

from interfaces import *

class PageTitleContentProvider(object):
    u"""
    Un Content Provider qui permet d'afficher le titre de la page (dans le header html)
    """
    implements(IContentProvider)
    adapts(Interface, IDefaultBrowserLayer, Interface)
    def __init__(self, context, request, view):
        self.context, self.request, self.view = context, request, view
        self._sitename = getSite().__name__ or "Zope3"
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
    The view that provides the logo and its html accessories
    """
    implements(IContentProvider)
    adapts(Interface, IDefaultBrowserLayer, Interface)
    def __init__(self, context, request, view):
        self.context, self.request, self.view = context, request, view
    def update(self):
        try:
            self.logo = getSite()['logo']
        except:
            self.logo=None
            self.url="#"
            self.title="Eztranet"
            return
        self.title = getSite().__name__
        self.url = AbsoluteURL(self.logo, self.request)()
    def render(self):
        u"Instead of rendering HTML, we return a dict with what we want to be traversed in TALES"
        return { 'url':self.url, 'title': self.title, 'alt':self.title }

class EztranetMainMenu(object):
    u"""
    The content provider that provides the main menu
    """
    implements(IContentProvider)
    adapts(Interface, IDefaultBrowserLayer, Interface)
    def __init__(self, context, request, view):
        self.context, self.request, self.view = context, request, view
    def update(self):
        site = getSite()
        self.menuitems = [ { 'name':site[i].title, 'url':AbsoluteURL(site[i], self.request)()} for i in site.keys() if i not in ['logo'] ]
        users = queryUtility(IAuthenticatorPlugin, name="EztranetUsers", context=site, default=None)
        if users and canAccess(users, '__name__'):
            self.menuitems.append({'name': u"Utilisateurs", 'url': AbsoluteURL(users, self.request)() + "/contents.html"})
    def render(self):
        return self.menuitems
