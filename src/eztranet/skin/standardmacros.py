# -*- coding: utf-8 -*-
from zope.publisher.browser import BrowserView
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.basicskin.standardmacros import StandardMacros

class MyOwnStandardMacros(StandardMacros):
    """
    implementation for the standard_macros view
    """
    macro_pages=('mymainmacro', 'rotterdamtree')

class MyMainMacro(BrowserView):
    """
    the view that allows to provide the custom macros defined in a template
    """
    template = ViewPageTemplateFile("main_template.pt")
    def __getitem__(self, key):
        return self.template.macros[key]
