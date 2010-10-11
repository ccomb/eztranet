from interfaces import IEztranetSiteManagerSetEvent, IEztranetSite, IInitialSetup
from z3c.form.field import Fields
from z3c.form.form import applyChanges
from z3c.formui.form import AddForm
from z3c.pagelet.browser import BrowserPagelet
from zope.app.component.site import LocalSiteManager, SiteManagerContainer
from zope.app.container.interfaces import IObjectAddedEvent, INameChooser
from zope.app.folder.folder import Folder
from zope.app.generations.utility import findObjectsProviding
from zope.intid import IntIds
from zope.intid.interfaces import IIntIds
from zope.component import adapter, getUtilitiesFor
from zope.component import createObject
from zope.event import notify
from zope.i18nmessageid import MessageFactory
from zope.interface import implements, Interface
import logging

_ = MessageFactory('eztranet')
logger = logging.getLogger(__name__)


class EztranetSiteManagerSetEvent(object):
    """event received when the site manager is set
    """
    implements(IEztranetSiteManagerSetEvent)
    def __init__(self, site):
        self.object=site


class EztranetSite(Folder, SiteManagerContainer):
    """The main container object

    We add an eztranet site, then we trigger a subscriber when adding it that
    will turn it into a site. Then another event is triggered that calls another
    subscriber which do the necessary to make the site work
    """

    implements(IEztranetSite)
    title = u''

    def setSiteManager(self, sm):
        "we add an event"
        super(EztranetSite, self).setSiteManager(sm)
        notify(EztranetSiteManagerSetEvent(self))


@adapter(IEztranetSite, IObjectAddedEvent)
def newEztranetSiteAdded(site, event):
    """a subscriber that do the necessary after the site is added
    """
    site.setSiteManager(LocalSiteManager(site))


@adapter(IEztranetSiteManagerSetEvent)
def EztranetInitialSetup(event):
    """create the initial objects required by the site
    """
    site=event.object
    sm = site.getSiteManager()

    # create and register the intid utility
    intid = IntIds()
    sm['unique integer IDs']=intid
    sm.registerUtility(intid, IIntIds)

    # then create the project folder
    event.object['projects'] = createObject('eztranet.ProjectContainer')
    event.object['projects'].title = _(u'Projects')

    # this setup could be done in an event triggered when adding the eztranet
    # by saying that EztranetSite implements a marker interface such as IHaveUserManagement
    #By now, we just run all the utilities providing IInitialSetup
    for utility_name, utility in getUtilitiesFor(IInitialSetup):
        logger.info(u'Running initial setup from %s' % utility.__module__)
        utility(site)

    #create an intid for all objects added in content space and site manager. (the intid is not yet active)"
    #KEEP THIS AT THE BOTTOM"
    for object in findObjectsProviding(site,Interface):
        intid.register(object)
    for object in findObjectsProviding(sm,Interface):
        intid.register(object)


class EztranetSiteAdd(AddForm):
    """Form to add a new eztranet site
    """
    fields = Fields(IEztranetSite)
    fields['__name__'].field.title = _(u'Name (used in the URL)')
    fields['__name__'].field.description = _(u'Name used in the URL')
    label = _(u'Adding an Eztranet Site')

    def create(self, data):
        eztranet_site = EztranetSite()
        applyChanges(self, eztranet_site, data)
        return eztranet_site
    def add(self, eztranet_site):
        name = INameChooser(self.context).chooseName(eztranet_site.__name__,
                                                     eztranet_site)
        self.context[name] = eztranet_site
        #return self.request.response.redirect('/')

    def nextURL(self):
        return '/'


class RootFolderView(BrowserPagelet):
    """View of the zodb root object. Used when there is no eztranet
    """
    def eztranet_sites(self):
        return [eztranet[0] for eztranet in self.context.items()
                if IEztranetSite.providedBy(eztranet[1])]



