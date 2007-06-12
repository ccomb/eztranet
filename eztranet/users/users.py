# -*- coding: utf-8 -*-
from zope.app.folder.folder import Folder
from zope.interface import implements, Interface
from zope.app.component.site import LocalSiteManager, SiteManagerContainer
from zope.component import adapter, adapts
from zope.app.container.interfaces import IObjectAddedEvent, IObjectRemovedEvent
from zope.event import notify
from zope.app.intid.interfaces import IIntIds
from zope.app.intid import IntIds
from zope.app.catalog.catalog import Catalog, ICatalog
from zope.app.catalog.text import TextIndex
from zope.component import createObject
from zope.app.generations.utility import findObjectsProviding
from zope.app.authentication import PluggableAuthentication
from zope.app.security.interfaces import IAuthentication
from zope.app.authentication.interfaces import IAuthenticatorPlugin
from zope.component import getUtility
from zope.app.container.interfaces import INameChooser
from zope.app.container.contained import NameChooser
from zope.app.authentication.principalfolder import InternalPrincipal, IInternalPrincipal, PrincipalFolder
from zope.app.securitypolicy.interfaces import IRole, IPrincipalRoleManager
from zope.app.component.hooks import getSite
from zope.traversing.browser.absoluteurl import AbsoluteURL
from zope.publisher.browser import TestRequest
from zope.component.factory import Factory

import string

from interfaces import *

class EztranetUsersContainer(PrincipalFolder):
    implements(IEztranetUsersContainer)
    __name__=__parent__=None

class EztranetUser(InternalPrincipal):
    u"""
    an eztranet user, ie a basic Principal that can be assigned an admin role
    """
    implements(IEztranetUser)
    passwordManagerName = 'MD5'
    def __getattr__(self, name):
        if name == 'IsAdmin':
            srm = IPrincipalRoleManager(getSite()) # The rolemanager of the site
            return srm.getSetting("eztranet.Administrator", self.login).getName()=="Allow"
        return super(EztranetUser, self).__getattr__(name)
    def __setattr__(self, name, value):
        if name == 'IsAdmin':
            srm = IPrincipalRoleManager(getSite()) # The rolemanager of the site
            if value:
                srm.assignRoleToPrincipal("eztranet.Administrator", self.login)
            else :
                srm.unsetRoleForPrincipal("eztranet.Administrator", self.login)
        else:
            super(EztranetUser, self).__setattr__(name, value)

EztranetUserFactory=Factory(EztranetUser)

@adapter(IEztranetUser, IObjectAddedEvent)
def EztranetUserAdded(user, event):
    u"a subscriber that do the necessary after a user has been added"
    srm = IPrincipalRoleManager(getSite()) # The rolemanager of the site
    srm.assignRoleToPrincipal("eztranet.Member", user.login)

@adapter(IEztranetUser, IObjectRemovedEvent)
def EztranetUserRemoved(user, event):
    u"""
    A subscriber that do the necessary after a user has been added
    We loop on every project and remove role assignment.
    """
    for project in getSite()['projects'].values():
        rolemanager = IPrincipalRoleManager(project)
        roles = rolemanager.getRolesForPrincipal(user.login)
        for role in roles:
            rolemanager.unsetRoleForPrincipal(role[0], user.login)

def initial_setup(site):
    sm = site.getSiteManager()
    # create and register the PAU (Pluggable Auth Utility)
    pau = PluggableAuthentication()
    sm['authentication'] = pau
    sm.registerUtility(pau, IAuthentication)
    # and the auth plugin
    users = EztranetUsersContainer()
    sm['authentication']['EztranetUsers'] = users
    sm.registerUtility(users, IAuthenticatorPlugin, name="EztranetUsers")
    # activate the auth plugins in the pau
    pau.authenticatorPlugins = (users.__name__, ) # a tuple with one element
    #activate the wanted credential plugins
    pau.credentialsPlugins = ( "No Challenge if Authenticated", "Session Credentials" )

class UserNameChooser(NameChooser):
    u"""
    adapter that allows to choose the __name__ of a user
    """
    implements(INameChooser)
    adapts(IEztranetUser)
    def chooseName(self, name, user):
        if not name and user is None:
            raise "UserNameChooser Error"
        if name:
            rawname = name
        if user is not None and len(user.login)>0:
            rawname = user.login
        return string.lower(rawname).strip().replace(' ','-').replace(u'/',u'-').lstrip('+@')
    def checkName(self, name, project):
        if user.__parent__ is not None and name in user.__parent__ and user is not user.__parent__['name']:
            return False
        else :
            return True
