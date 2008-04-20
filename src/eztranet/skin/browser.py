from zope.traversing.browser.absoluteurl import AbsoluteURL
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import implements, Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.app.component.hooks import getSite
from zope.component import adapts, queryUtility
from zope.security.checker import canAccess
from zope.app.authentication.interfaces import IAuthenticatorPlugin
from zope.publisher.browser import BrowserPage
from zope.app.pagetemplate import ViewPageTemplateFile

class PageTitleContentProvider(object):
    """
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
            if self.context.__name__ == 'eztranet':
                self._pagetitle = 'Eztranet : votre extranet photo video'
        else:
            self._pagetitle = self._sitename
    def render(self):
        return self._pagetitle

class LogoProvider(object):
    """
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
            self.logo = None
            self.url = "#"
            self.title = "Eztranet"
            return
        self.title = getSite().__name__
        self.url = AbsoluteURL(self.logo, self.request)()
    def render(self):
        """
        Instead of rendering HTML,
        we return a dict with what we want to be traversed in TALES
        """
        return { 'url':self.url, 'title': self.title, 'alt':self.title }

class EztranetMainMenu(object):
    """
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
            self.menuitems.append({'name': u'Users', 'url': AbsoluteURL(users, self.request)() + "/contents.html"})
    def render(self):
        return self.menuitems

class RootFolderView(BrowserPage):
    __call__ = ViewPageTemplateFile('rootfolder.pt')
    def eztranet_sites(self):
        return list(self.context.keys())
