from zope.interface import Attribute
from zope.app.container.interfaces import IContainer, IContained
from zope.app.container.constraints import contains, containers
from zope.schema import Bool
from zope.app.authentication.principalfolder import IInternalPrincipal, IInternalPrincipalContainer
from zope.app.authentication.interfaces import IAuthenticatorPlugin
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('eztranet')

class IEztranetUsersContainer(IInternalPrincipalContainer, IAuthenticatorPlugin, IContainer, IContained):
    contains("eztranet.users.interfaces.IEztranetUser")
    title = Attribute(u'title of the users container')

class IEztranetUser(IInternalPrincipal):
    """
    A user of the eztranet. This is an extended Principal
    """
    containers(IEztranetUsersContainer)
    IsAdmin = Bool(_(u'Administrator'))
