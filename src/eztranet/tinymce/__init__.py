from zope.app.pagetemplate import ViewPageTemplateFile
from zope.interface import implements
from zope.schema import Text
from zope.schema.interfaces import IField

class IHtmlText(IField):
    """An html text field
    """


class HtmlText(Text):
    """Field describing an html text field
    """
    implements(IHtmlText)
    
    def _validate(self, value):
        super(HtmlText, self)._validate(value)


class TinyHeader(object):
    """content provider for the tinymce js
    """
    template = ViewPageTemplateFile('header.pt')

    def update(self):
        pass

    def render(self):
        return self.template(self)
