from zope.interface import Interface
from zope.app.container.interfaces import IContainer, IContained
from zope.app.component.interfaces import IPossibleSite
from zope.component.interfaces import IObjectEvent
from zope.schema import TextLine
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('eztranet')


class IEztranetSite(IPossibleSite, IContainer, IContained):
    """
    The interface of the main eztranet site container
    """
    title = TextLine(title=_(u'Title (used for display)'),
                     description=_(u'The name of your Eztranet Site'))

class IEztranetSiteManagerSetEvent(IObjectEvent):
    """
    The event fired when a eztranet site is added.
    The subscriber must create the objects and utilities required to running the site
    in particular the IntId, the catalog and indices, the trash, etc.
    """ 

class IConfigurator(Interface):
    """
    The interface of the root dummy configuration object
    """

class IInitialSetup(Interface):
    """
    The interface of each initial setup utility
    """

