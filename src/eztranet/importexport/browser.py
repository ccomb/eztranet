from __future__ import with_statement
from contextlib import contextmanager
from eztranet.project.interfaces import ILargeBytes
from eztranet.project.interfaces import IProjectItem
from interfaces import IExport, IImport
from z3c.form.field import Fields
from z3c.form.interfaces import IValidator
from z3c.form.validator import SimpleFieldValidator
from z3c.formui.form import AddForm
from z3c.menu.simple.menu import SimpleMenuItem
from z3c.pagelet.browser import BrowserPagelet
from zope.component import getAdapter, adapts
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
from zope.interface import implements, Interface
from zope.publisher.browser import BrowserView, FileUpload
from zope.security.checker import canWrite
import os, tempfile, copy

_ = MessageFactory('eztranet')

class ImportExportPage(AddForm):
    """Page to export a folder as a zip file
    This page should display a selection form to choose the export format.
    The export format would be generated from the registered export utilities,
    and transmitted via a POST argument.
    It should also offer select boxes to choose the features to export
    We first export only as a zip file.
    """
    fields = Fields(IProjectItem).omit('__name__', '__parent__',
                                       'title', 'description')
    id = "addform"
    valid_zip = True
    import_allowed = False
    buttons = copy.deepcopy(AddForm.buttons)
    buttons['add'].title = _(u'Import zip')

    def __init__(self, context, request):
        self.context, self.request = context, request
        BrowserPagelet.__init__(self, context, request)
        AddForm.__init__(self, context, request)

        # import allowed?
        if canWrite(self.context, 'title'):
            self.import_allowed = True

    def createAndAdd(self, data):
        if not self.import_allowed: return
        if ('data' in data
                and type(data['data']) is FileUpload):
            uploaded_file = data['data']
            try:
                getAdapter(self.context, IImport, name=u'zip').do_import(uploaded_file.name)
            except:
                self.valid_zip = False


@contextmanager
def autoclean(somefile):
    yield somefile
    somefile.close()
    os.remove(somefile.name)


class ExportDownload(BrowserView):
    """the actual view that creates and returns the zip file
    """
    filename = None
    def __call__(self):
        if 'do_export' not in self.request:
            return self.request.response.redirect('.')
        #choose a temp path to export
        fd, self.filename = tempfile.mkstemp()
        os.close(fd)
        export_adapter = getAdapter(self.context, IExport, 'zip')
        export_adapter.do_export(self.filename)

        self.request.response.setHeader(
                'Content-disposition',
                'attachment; filename="%s"' % (self.context.__name__ + '.zip').encode('utf-8'))
        filesize = os.stat_result(os.stat(self.filename)).st_size
        self.request.response.setHeader('Content-length',
                                        filesize)
        self.request.response.setHeader('Content-Type', 'application/zip')
        with autoclean(open(self.filename)) as zipfile:
            return zipfile.read()



class ExportPageMenuItem(SimpleMenuItem):
    title = _(u'Imp/exp')
    url = 'importexport.html'
    weight = 900


class FileUploadHeader(object):
    """Content provider for the js header of gp.fileupload"""

    def update(self):
        pass

    def render(self):
        submit_label = _(u'Send files...')
        link_label = _(u'Add more files...')
        return """
        <script type="text/javascript"
                src="/gp.fileupload.static/jquery.js"></script><script
                type="text/javascript"
                src="/gp.fileupload.static/jquery.fileupload.js">
        </script>
        <script type="text/javascript">
            jQuery(document).ready(function() {
                jQuery('#addform').fileUpload({
                    stat_delay: 500,
                    action:'importexport.html',
                    field_name:'form.widgets.data',
                    hidden_submit_name:'form.buttons.add',
                    replace_existing_form: false,
                    submit_label:'%s',
                    link_label:'%s'});
            });
        </script>
        """ % (translate(submit_label, context=self.request),
               translate(link_label, context=self.request))


class BigFileValidator(SimpleFieldValidator):
    implements(IValidator)
    adapts(
        Interface,
        Interface,
        ImportExportPage,
        ILargeBytes,
        Interface)

    def validate(self, data):
        return type(data) is FileUpload
