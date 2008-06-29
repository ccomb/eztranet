# -*- coding: utf-8 -*-
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import implements, Interface
from zope.app.component.hooks import getSite
from zope.component import adapts, queryUtility
from zope.security.checker import canAccess
from zope.app.authentication.interfaces import IAuthenticatorPlugin
from zope.publisher.browser import BrowserPage
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('eztranet')
from interfaces import IEztranetSkin

class PageTitleContentProvider(object):
    """
    A Content Provider that allows to display the page titlee (in the html header)
    """
    implements(IContentProvider)
    adapts(Interface, IEztranetSkin, Interface)
    def __init__(self, context, request, view):
        self.context, self.request, self.view = context, request, view
        self._sitename = getSite().__name__ or "Zope3"
    def update(self):
        # we retrieve the name of the context if any
        if hasattr(self.context,'__name__') and self.context.__name__ is not None:
            self._pagetitle = self.context.__name__ + " - " + self._sitename
            if self.context.__name__ == 'eztranet':
                self._pagetitle = _(u'Eztranet : your photo/video extranet')
            if self.context.__name__ == 'EztranetUsers':
                self._pagetitle = _(u'Users')
        else:
            self._pagetitle = self._sitename
    def render(self):
        return self._pagetitle

class LogoProvider(object):
    """
    The view that provides the logo and its html accessories
    """
    implements(IContentProvider)
    adapts(Interface, IEztranetSkin, Interface)
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
        self.url = absoluteURL(self.logo, self.request)
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
    adapts(Interface, IEztranetSkin, Interface)
    def __init__(self, context, request, view):
        self.context, self.request, self.view = context, request, view
        self.menuitems = []
    def update(self):
        site = getSite()
        if site is not None:
            self.menuitems = [{'name':site[i].title,
                               'url':absoluteURL(site[i], self.request)}
                               for i in site.keys() if i not in ['logo']]
            users = queryUtility(IAuthenticatorPlugin, name="EztranetUsers", context=site, default=None)
            if users is not None and canAccess(users, '__name__'):
                self.menuitems.append({'name': _(u'Users'),
                                       'url': absoluteURL(users, self.request) + '/contents.html'})
    def render(self):
        return self.menuitems

class RootFolderView(BrowserPage):
    __call__ = ViewPageTemplateFile('rootfolder.pt')
    def eztranet_sites(self):
        return list(self.context.keys())

class LangChoiceContentProvider(object):
    """
    Content provider that allows to choose the language::
    
    >>> from eztranet.skin.browser import LangChoiceContentProvider
    >>> from zope.publisher.browser import TestRequest
    >>> dummyrequest = TestRequest(PATH_INFO='/eztranet/projects')
    >>> import zope.app.folder
    >>> root = zope.app.folder.folder.rootFolder()
    >>> root.__name__ = u'root'
    >>> root['foo'] = zope.app.folder.Folder()
    >>> root['foo'].__parent__ = root
    >>> dummyobj = root['bar'] = zope.app.folder.Folder()
    >>> dummyobj.__parent__ = root['foo']
    >>> from zope.publisher.browser import BrowserPage
    >>> dummyview = BrowserPage(dummyobj, dummyrequest)
    >>> dummyview.__name__ = 'index.html'
    >>> LangChoiceContentProvider(dummyobj, dummyrequest, dummyview).lang is None
    True
    >>> dummyrequest = TestRequest(PATH_INFO='/++lang++fr/eztranet/projects')
    >>> LangChoiceContentProvider(dummyobj, dummyrequest, dummyview).lang
    u'fr'
    >>> dummyrequest = TestRequest(PATH_INFO='/++lang++en/eztranet/projects')
    >>> LangChoiceContentProvider(dummyobj, dummyrequest, dummyview).lang
    u'en'
    >>> dummyrequest = TestRequest(PATH_INFO='/++lang++xx/eztranet/projects')
    >>> LangChoiceContentProvider(dummyobj, dummyrequest, dummyview).lang
    u'xx'
    >>> dummyrequest = TestRequest(PATH_INFO='/++vh++http:eztranet.gorfou.fr:80/++/++lang++xx/eztranet/projects')
    >>> LangChoiceContentProvider(dummyobj, dummyrequest, dummyview).lang
    u'xx'
    >>> dummyrequest = TestRequest(PATH_INFO='/')
    >>> LangChoiceContentProvider(dummyobj, dummyrequest, dummyview).lang is None
    True
    >>> dummyrequest = TestRequest(PATH_INFO='/', langchoice='fr')
    >>> LangChoiceContentProvider(dummyobj, dummyrequest, dummyview).lang
    'fr'

    """
    implements(IContentProvider)
    adapts(Interface, IEztranetSkin, Interface)
    lang = None

    def __init__(self, context, request, view):
        self.context, self.request, self.view = context, request, view
        current_path = request.getURL(path_only=True)
        langindex = current_path.find('/++lang++')
        if langindex >= 0:
            # get the lang from the url
            self.lang = current_path[langindex+9:langindex+11]
            # rebuild the url without language
            current_path = current_path[:langindex] + current_path[langindex+11:]
        if 'langchoice' in self.request:
            # if we asked for a language, we must redirect to it
            self.lang = self.request['langchoice'][:2]
            if self.request['langchoice'] == 'auto':
                self.lang = None
            if self.lang:
                current_path = '/++lang++' + self.lang + current_path
            self.request.response.redirect(current_path)

    def update(self):
        self.langs = {'en':u'english', 'fr':u'français'}

    def render(self):
       return ViewPageTemplateFile('languagechoice.pt')(self) 

