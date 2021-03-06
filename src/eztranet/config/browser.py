from eztranet.eztranet import EztranetSimpleMenuItem
from z3c.pagelet.browser import BrowserPagelet
#from z3c.menu.simple.menu import SimpleMenuItem
from z3c.formui.form import EditForm
from z3c.form.field import Fields
from interfaces import IConfigFormType
from zope.component import getUtilitiesFor
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('eztranet')

class ConfigPage(EditForm, BrowserPagelet):
    """configuration page for everything configurable on the context
    """
    @property
    def fields(self):
        """construct the fields from all the IConfigFormType interfaces
        """
        fields = Fields()
        for name,interface in getUtilitiesFor(IConfigFormType):
            fields += Fields(interface)
        return fields


class ConfigPageMenuItem(EztranetSimpleMenuItem):
    title = _(u'Config.')
    url = 'config.html'
    weight = 1000
    icon = '/@@/images/config.png'
