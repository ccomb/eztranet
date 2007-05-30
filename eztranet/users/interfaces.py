# -*- coding: utf-8 -*-
from zope.app.container.interfaces import IContainer, IContained
from zope.app.container.constraints import contains, containers
from zope.schema import List, TextLine, URI, Text, Choice, List, Bool
from zope.index.text.interfaces import ISearchableText
from zope.interface import Attribute, Interface
from zope.interface.interfaces import IInterface
from zope.app.file.interfaces import IFile
from zope.app.authentication.principalfolder import IInternalPrincipal, IInternalPrincipalContained


class IEztranetUser(Interface):
    u"""
    A user of the eztranet. This is an extended Principal
    """
    IsAdmin = Bool(u"Administrateur")