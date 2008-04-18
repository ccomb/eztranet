# -*- coding: utf-8 -*-
from zope.app.container.interfaces import IContainer, IContained
from zope.app.component.interfaces import IPossibleSite
from zope.component.interfaces import IObjectEvent
from zope.schema import TextLine


class IEztranetSite(IPossibleSite, IContainer, IContained):
    u"""
    The interface of the main eztranet site container
    """
    title = TextLine(title = u'Title (used for display)',
                     description = u'The name of your Eztranet Site')

class IEztranetSiteManagerSetEvent(IObjectEvent):
    u"""
    The event fired when a eztranet site is added.
    The subscriber must create the objects and utilities required to running the site
    in particular the IntId, the catalog and indices, the trash, etc.
    """ 

class IConfigurator(object):
    u"""
    The interface of the root dummy configuration object
    """