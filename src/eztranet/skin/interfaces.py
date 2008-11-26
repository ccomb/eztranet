from z3c.layer.pagelet import IPageletBrowserLayer
from zope.viewlet.interfaces import IViewletManager
from z3c.formui.interfaces import IDivFormLayer
from z3c.form.interfaces import IFormLayer

class IEztranetSkin(IDivFormLayer, IFormLayer, IPageletBrowserLayer):
  """The main skin of the application
  """

class IHeaders(IViewletManager):
    """Viewlet manager for headers (js, css, meta, etc.)
    """

class ITabMenu(IViewletManager):
    """The tab menu for the views
    """
