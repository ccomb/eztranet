# -*- coding: utf-8 -*-
from zope.app.container.interfaces import IContainer, IContained
from zope.app.container.constraints import contains, containers
from zope.schema import Bool
from zope.app.authentication.principalfolder import IInternalPrincipal, IInternalPrincipalContainer
from zope.app.authentication.interfaces import IAuthenticatorPlugin

class IEztranetUsersContainer(IInternalPrincipalContainer, IAuthenticatorPlugin, IContainer, IContained):
    contains("eztranet.users.interfaces.IEztranetUser")

class IEztranetUser(IInternalPrincipal):
    u"""
    A user of the eztranet. This is an extended Principal
    """
    containers(IEztranetUsersContainer)
    IsAdmin = Bool(u"Administrateur")