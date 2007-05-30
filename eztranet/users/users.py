# -*- coding: utf-8 -*-
from zope.app.folder.folder import Folder
from zope.interface import implements, Interface
from zope.app.component.site import LocalSiteManager, SiteManagerContainer
from zope.component import adapter, adapts
from zope.app.container.interfaces import IObjectAddedEvent
from zope.event import notify
from zope.app.intid.interfaces import IIntIds
from zope.app.intid import IntIds
from zope.app.catalog.catalog import Catalog, ICatalog
from zope.app.catalog.text import TextIndex
from zope.component import createObject
from zope.app.generations.utility import findObjectsProviding
from zope.app.authentication import PluggableAuthentication
from zope.app.security.interfaces import IAuthentication
from zope.app.authentication.principalfolder import PrincipalFolder
from zope.app.authentication.interfaces import IAuthenticatorPlugin
from zope.component import getUtility
from zope.app.container.interfaces import INameChooser
from zope.app.container.contained import NameChooser
from zope.app.authentication.principalfolder import InternalPrincipal, IInternalPrincipal
from zope.app.securitypolicy.interfaces import IRole, IPrincipalRoleManager
from zope.app.component.hooks import getSite
from zope.traversing.browser.absoluteurl import AbsoluteURL
from zope.publisher.browser import TestRequest

import string

from interfaces import *
   
class EztranetUser(InternalPrincipal):
    u"""
    an eztranet user, ie a basic Principal that can be assigned an admin role
    """
    implements(IInternalPrincipal)
    IsAdmin=False
    def __mmmmgetattr__(self, name):
        if name == 'IsAdmin':
            print "GET"
            srm = IPrincipalRoleManager(getSite()) # The rolemanager of the site
            return srm.getSetting(role, user).getName()=="Allow"
        else:
            return super(EztranetUser, self).__getattr__(name)
    def __mmmmmsetattr__(self, name, value):
        if name == 'IsAdmin':
            print "SET = %s" % value
            if value:
                print "ADMIN"
                srm = IPrincipalRoleManager(getSite()) # The rolemanager of the site
                srm.assignRoleToPrincipal("eztranet.Administrator", self)
        else:
            super(EztranetUser, self).__setattr__(name, value)

def initial_setup(site):
    sm = site.getSiteManager()
    # create and register the PAU (Pluggable Auth Utility)
    pau = PluggableAuthentication()
    site['authentication'] = pau
    sm.registerUtility(pau, IAuthentication)
    # and the auth plugin
    users = PrincipalFolder()
    site['authentication']['users'] = users
    sm.registerUtility(users, IAuthenticatorPlugin, name="users")
    # activate the auth plugins in the pau
    pau.authenticatorPlugins = (users.__name__)
    #activate the wanted credential plugins
    pau.credentialsPlugins = ( "No Challenge if Authenticated", "Session Credentials" )

class UserNameChooser(NameChooser):
    u"""
    adapter that allows to choose the __name__ of a user
    """
    implements(INameChooser)
    adapts(IInternalPrincipal)
    def chooseName(self, name, user):
        if not name and user is None:
            raise "UserNameChooser Error"
        if name:
            rawname = name
        if user is not None and len(user.title)>0:
            rawname = user.title
        return string.lower(rawname).strip().replace(' ','-').replace(u'/',u'-').lstrip('+@')
    def checkName(self, name, project):
        if user.__parent__ is not None and name in user.__parent__ and user is not user.__parent__['name']:
            return False
        else :
            return True