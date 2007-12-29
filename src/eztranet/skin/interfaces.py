# -*- coding: utf-8 -*-
from zope.publisher.interfaces.browser import IDefaultBrowserLayer



class IEztranetSkin(IDefaultBrowserLayer):
  """
  the main skin of the application
  We cannot provide IBrowserSkinType here because this interface must be registered with a name (the name of the skin)
  So it is registered for IBrowserSkinType in ZCML.
  This skin is activated by default with overrides zcml
  """
