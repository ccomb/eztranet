from interfaces import IEztranetSiteManagerSetEvent, IEztranetSite
from zope.app.folder.folder import Folder
from zope.interface import implements, Interface
from zope.app.component.site import LocalSiteManager, SiteManagerContainer
from zope.component import adapter
from zope.app.container.interfaces import IObjectAddedEvent, INameChooser
from zope.event import notify
from zope.app.intid.interfaces import IIntIds
from zope.app.intid import IntIds
from zope.component import createObject
from zope.app.generations.utility import findObjectsProviding
from users import users
from zope.formlib.form import AddForm, Fields, applyChanges
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('eztranet')

class EztranetSiteManagerSetEvent(object):
    implements(IEztranetSiteManagerSetEvent)
    def __init__(self, site):
        self.object=site

class EztranetSite(Folder, SiteManagerContainer):
    """
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
    "a subscriber that do the necessary after the site is added"
    site.setSiteManager(LocalSiteManager(site))

@adapter(IEztranetSiteManagerSetEvent)
def EztranetInitialSetup(event):
    "create the initial objects required by the site"
    # do the necessary!
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
    users.initial_setup(site)
    
    #create an intid for all objects added in content space and site manager. (the intid is not yet active)"
    #KEEP THIS AT THE BOTTOM"
    for object in findObjectsProviding(site,Interface):
        intid.register(object)
    for object in findObjectsProviding(sm,Interface):
        intid.register(object)

class EztranetSiteAdd(AddForm):
    form_fields = Fields(IEztranetSite)
    form_fields['__name__'].field.title = _(u'Name (used in the URL)')
    form_fields['__name__'].field.description = _(u'Name used in the URL')
    label = _(u'Adding an Eztranet Site')

    def create(self, data):
        eztranet_site = EztranetSite()
        applyChanges(eztranet_site, self.form_fields, data)
        self.context.contentName = INameChooser(self.context.context).\
                                    chooseName(eztranet_site.__name__,
                                               eztranet_site)
        return eztranet_site



