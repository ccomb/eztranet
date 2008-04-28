from zope.interface import implements
from zope.component import adapter, adapts
from zope.app.container.interfaces import IObjectAddedEvent, IObjectRemovedEvent, INameChooser
from zope.app.container.contained import NameChooser
from zope.app.authentication import PluggableAuthentication
from zope.app.authentication.interfaces import IAuthenticatorPlugin
from zope.component.factory import Factory
from zope.app.authentication.principalfolder import InternalPrincipal, PrincipalFolder
from zope.app.security.interfaces import IAuthentication
from zope.securitypolicy.interfaces import IPrincipalRoleManager
from zope.app.component.hooks import getSite
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('eztranet')

from interfaces import IEztranetUsersContainer, IEztranetUser

class EztranetUsersContainer(PrincipalFolder):
    implements(IEztranetUsersContainer)
    __name__=__parent__=None

class EztranetUser(InternalPrincipal):
    """
    an eztranet user, ie a basic Principal that can be assigned an admin role
    """
    implements(IEztranetUser)
    passwordManagerName = 'MD5'

    def _getAdminStatus(self):
        srm = IPrincipalRoleManager(getSite()) # The rolemanager of the site
        return srm.getSetting("eztranet.Administrator", self.login).getName()=="Allow"

    def _setAdminStatus(self, value):
        srm = IPrincipalRoleManager(getSite()) # The rolemanager of the site
        if value:
            srm.assignRoleToPrincipal("eztranet.Administrator", self.login)
        else :
            srm.unsetRoleForPrincipal("eztranet.Administrator", self.login)

    IsAdmin = property(_getAdminStatus, _setAdminStatus)

EztranetUserFactory=Factory(EztranetUser)

@adapter(IEztranetUser, IObjectAddedEvent)
def EztranetUserAdded(user, event):
    """
    a subscriber that do the necessary after a user has been added
    """
    srm = IPrincipalRoleManager(getSite()) # The rolemanager of the site
    srm.assignRoleToPrincipal('eztranet.Member', user.login)

def recursively_unsetrole(obj, userlogin):
    """
    function used to recurse the role removal on all objects
    """
    rolemanager = IPrincipalRoleManager(obj)
    roles = rolemanager.getRolesForPrincipal(userlogin)
    for role in roles:
        rolemanager.unsetRoleForPrincipal(role[0], userlogin)
    for subobj in obj.values():
        recursively_unsetrole(subobj, userlogin)

@adapter(IEztranetUser, IObjectRemovedEvent)
def EztranetUserRemoved(user, event):
    """
    A subscriber that do the necessary after a user has been added
    We loop on every project and remove role assignment.
    """
    site = getSite()
    if 'projects' in site:
        for project in getSite()['projects'].values():
            recursively_unsetrole(project, user.login)

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
    pau.credentialsPlugins = ('No Challenge if Authenticated',
                              'Session Credentials' )
    # create an admin user to be able to log in
    admin = EztranetUser('admin',
                         'eztranet',
                         _(u'eztranet initial administrator'),
                         passwordManagerName='MD5')
    # grant him the admin role
    srm = IPrincipalRoleManager(site)
    srm.assignRoleToPrincipal("eztranet.Administrator",
                              admin.login)
    srm.assignRoleToPrincipal("eztranet.Member",
                              admin.login)
    users[admin.login] = admin

class UserNameChooser(NameChooser):
    """
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
        return rawname.strip().replace(' ','-').replace(u'/',u'-').lstrip('+@')

