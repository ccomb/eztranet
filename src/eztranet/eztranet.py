# -*- coding: utf-8 -*-
from interfaces import IEztranetSiteManagerSetEvent, IEztranetSite
from zope.app.folder.folder import Folder
from zope.interface import implements, Interface
from zope.app.component.site import LocalSiteManager, SiteManagerContainer
from zope.component import adapter
from zope.app.container.interfaces import IObjectAddedEvent, INameChooser
from zope.event import notify
from zope.app.intid.interfaces import IIntIds
from zope.app.intid import IntIds
from zope.app.catalog.catalog import Catalog, ICatalog
from zope.app.catalog.text import TextIndex
from zope.component import createObject
from zope.app.generations.utility import findObjectsProviding
from project.interfaces import ISearchableTextOfProject
from project.interfaces import ISearchableTextOfProjectItem
from users import users
from zope.formlib.form import AddForm, Fields, applyChanges

class EztranetSiteManagerSetEvent(object):
    implements(IEztranetSiteManagerSetEvent)
    def __init__(self, site):
        self.object=site

class EztranetSite(Folder, SiteManagerContainer):
    u"""
    Le principe est qu'on ajoute un site eztranet,
    puis on déclenche un subscriber au moment de l'ajout qui va le transformer en site.
    A ce moment un evenement est déclenché et appelle un autre subscriber qui va
    créer le nécessaire pour faire fonctionner le site
    """
    implements(IEztranetSite)
    title = u''

    def setSiteManager(self, sm):
        u"on surcharge cette méthode pour pouvoir lancer l'evenement"
        super(EztranetSite, self).setSiteManager(sm)
        notify(EztranetSiteManagerSetEvent(self))

@adapter(IEztranetSite, IObjectAddedEvent)
def newEztranetSiteAdded(site, event):
    u"a subscriber that do the necessary after the site is added"
    site.setSiteManager(LocalSiteManager(site))

@adapter(IEztranetSiteManagerSetEvent)
def EztranetInitialSetup(event):
    u"create the initial objects required by the site"
    # do the necessary!
    site=event.object
    sm = site.getSiteManager()
    
    # create and register the intid utility
    intid = IntIds()
    sm['unique integer IDs']=intid
    sm.registerUtility(intid, IIntIds)
    
    # then create the project folder
    event.object['projects'] = createObject(u"eztranet.ProjectContainer")
    event.object['projects'].title = u"Projects"
     
    # then create and register the catalog
    catalog = Catalog()
    sm['catalog']=catalog
    sm.registerUtility(catalog, ICatalog)
     
    # then create and register the wanted indices in the catalog
    catalog['project_text'] = TextIndex(interface=ISearchableTextOfProject, field_name='getSearchableText', field_callable=True)
    catalog['projectitem_text'] = TextIndex(interface=ISearchableTextOfProjectItem, field_name='getSearchableText', field_callable=True)
    
    # cet setup pourrait être fait dans un event déclenché lors de l'ajout du EztranetSite
    # en disant que l'EztranetSite implémente une interface marqueur du style IHaveUserManagement
    users.initial_setup(site)
    
    #create an intid for all objects added in content space and site manager. (the intid is not yet active)"
    #KEEP THIS AT THE BOTTOM"
    for object in findObjectsProviding(site,Interface):
        intid.register(object)
    for object in findObjectsProviding(sm,Interface):
        intid.register(object)
    # reindex eveything
    catalog.updateIndexes()

class EztranetSiteAdd(AddForm):
    form_fields = Fields(IEztranetSite)
    form_fields['__name__'].field.title = u'Name (used in the URL)'
    form_fields['__name__'].field.description = u'Name used in the URL'
    label = u"Adding an Eztranet Site"

    def create(self, data):
        eztranet_site = EztranetSite()
        applyChanges(eztranet_site, self.form_fields, data)
        self.context.contentName = INameChooser(self.context.context).\
                                    chooseName(eztranet_site.__name__,
                                               eztranet_site)
        return eztranet_site



