# -*- coding: utf-8 -*-
from interfaces import IEztranetSkin
from interfaces import ITabMenu
from z3c.pagelet.browser import BrowserPagelet
from zope.app.authentication.interfaces import IAuthenticatorPlugin
from zope.app.component.hooks import getSite
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.component import adapts, queryUtility
from zope.contentprovider.interfaces import IContentProvider
from zope.i18nmessageid import MessageFactory
from zope.interface import implements, Interface
from zope.security.checker import canAccess
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.viewlet.manager import WeightOrderedViewletManager
from pkg_resources import get_distribution

_ = MessageFactory('eztranet')

class EztranetSiteView(BrowserPagelet):
    """The view of the eztranet object, ie the homepage"""

class TabMenu(WeightOrderedViewletManager):
    """the tabbed menu"""
    implements(ITabMenu)

class PageTitleContentProvider(object):
    """A Content Provider that allows to display the page title (in the html header)"""

    implements(IContentProvider)
    adapts(Interface, IEztranetSkin, Interface)
    def __init__(self, context, request, view):
        self.context, self.request, self.__parent__ = context, request, view
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
    """The view that provides the logo and its html accessories"""

    implements(IContentProvider)
    adapts(Interface, IEztranetSkin, Interface)
    def __init__(self, context, request, view):
        self.context, self.request, self.__parent__ = context, request, view
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
    """The content provider that provides the main menu"""

    implements(IContentProvider)
    adapts(Interface, IEztranetSkin, Interface)
    def __init__(self, context, request, view):
        self.context, self.request, self.__parent__ = context, request, view
        self.menuitems = []
    def update(self):
        site = getSite()
        if site is not None:
            self.menuitems = [{'name':hasattr(site[i],'title') and site[i].title or site[i].__name__,
                               'url':absoluteURL(site[i], self.request)}
                               for i in site.keys() if i not in ['logo']]
            users = queryUtility(IAuthenticatorPlugin,
                                 name="EztranetUsers",
                                 context=site,
                                 default=None)
            if users is not None and canAccess(users, '__name__'):
                self.menuitems.append({'name': _(u'Users'),
                                       'url': absoluteURL(users, self.request) + '/contents.html'})
    def render(self):
        return self.menuitems

class LangChoiceContentProvider(object):
    """Content provider that allows to choose the language"""

    implements(IContentProvider)
    adapts(Interface, IEztranetSkin, Interface)
    lang = None

    def __init__(self, context, request, view):
        self.context, self.request, self.__parent__ = context, request, view
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


class VersionNumberProvider(object):
    """Content provider that gives the version number of the program """
    
    implements(IContentProvider)
    adapts(Interface, IEztranetSkin, Interface)

    def __init__(self, context, request, view):
        self.context, self.request, self.__parent__ = context, request, view

    def update(self):
        self.version = get_distribution('eztranet').version

    def render(self):
       return self.version 
