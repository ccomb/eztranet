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
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('eztranet')

class PageTitleContentProvider(object):
    """
    A Content Provider that allows to display the page titlee (in the html header)
    """
    implements(IContentProvider)
    adapts(Interface, IDefaultBrowserLayer, Interface)
    def __init__(self, context, request, view):
        self.context, self.request, self.view = context, request, view
        self._sitename = getSite().__name__ or "Zope3"
    def update(self):
        # we retrieve the name of the context if any
        if hasattr(self.context,'__name__') and self.context.__name__ is not None:
            self._pagetitle = self.context.__name__ + " - " + self._sitename
            if self.context.__name__ == 'eztranet':
                self._pagetitle = _(u'Eztranet : your photo/video extranet')
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
            self.title = u'Eztranet'
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
        self.menuitems = [{'name':site[i].title,
                           'url':AbsoluteURL(site[i], self.request)()}
                          for i in site.keys() if i not in ['logo']]
        users = queryUtility(IAuthenticatorPlugin, name="EztranetUsers", context=site, default=None)
        if users and canAccess(users, '__name__'):
            self.menuitems.append({'name': _(u'Users'),
                                   'url': AbsoluteURL(users, self.request)() + '/contents.html'})
    def render(self):
        return self.menuitems

class RootFolderView(BrowserPage):
    __call__ = ViewPageTemplateFile('rootfolder.pt')
    def eztranet_sites(self):
        return list(self.context.keys())
