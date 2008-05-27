from zope.app.form.browser.textwidgets import FileWidget
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

class MultiUploadWidget(FileWidget):
    __call__ = ViewPageTemplateFile("multiupload.pt")


