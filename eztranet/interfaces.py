# -*- coding: utf-8 -*-
from zope.app.container.interfaces import IContainer
from zope.app.component.interfaces import IPossibleSite
from zope.component.interfaces import IObjectEvent


class IEztranetSite(IPossibleSite, IContainer):
    u"""
    The (empty) interface of the main eztranet site container
    This interface could be used to define high-level functions
    to abstract the object hierarchy. (for ex accessing organizations).
    """

class IEztranetSiteManagerSetEvent(IObjectEvent):
    u"""
    The event fired when a eztranet site is added.
    The subscriber must create the objects and utilities required to running the site
    in particular the IntId, the catalog and indices, the trash, etc.
    """ 

