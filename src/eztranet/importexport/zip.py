from hachoir_parser import createParser
from interfaces import IExportable, IExport
from interfaces import IImportable, IImport
from os.path import basename
from zope.app.container.interfaces import IContainer
from zope.component import createObject, adapts
from zope.file.interfaces import IFile
from zope.interface import implements
from zope.lifecycleevent import ObjectCreatedEvent
import zipfile, os, tempfile
import zope.event
import zope.publisher

class ZipImport(object):
    """Import plugin that uncompresses a zipfile into file and folder objects
    """
    implements(IImport)
    adapts(IImportable)

    def __init__(self, context):
        self.context = context

    def do_import(self, filename):
        """FIXME : redundancy with createAndAdd from project.browser.browser.py
        """
        zfile = zipfile.ZipFile(filename)
        for f in zfile.infolist():
            # we recreate the hierarchy to the object
            current_object = self.context
            for d in f.filename.split(os.path.sep)[:-1]:
                if d is '': continue
                if d not in current_object:
                    current_object[d] = createObject('folder')
                    current_object[d].__name__ = d
                    current_object[d].title = d
                current_object = current_object[d]
            objname = f.filename.split(os.path.sep)[-1]
            if objname not in current_object:
                # we extract the archive member in a temporary file
                fd, filename = tempfile.mkstemp()
                tmpfile = os.fdopen(fd, 'w')
                tmpfile.write(zfile.read(f.filename))
                tmpfile.close()

                # we determine the file type
                hachoir_parser = createParser(unicode(filename))
                if hachoir_parser is None:
                    mimetype = 'application/data'
                    majormimetype = 'file'
                else:
                    mimetype = hachoir_parser.mime_type
                    majormimetype = mimetype.split('/')[0]

                # we create the object with a registered factory
                # whose name is the major mimetype
                item = createObject(majormimetype)

                item.title = item.__name__ = objname
                # set some file attributes
                major, minor, parameters = zope.publisher.contenttype.parse(
                                                                         mimetype)
                if 'charset' in parameters:
                    parameters['charset'] = parameters['charset'].lower()
                item.mimeType = mimetype
                item.parameters = parameters


                # now we import the file into the object with an adapter
                IImport(item).do_import(filename)
                current_object[objname] = item
                os.remove(filename)

                # notify the file is added
                zope.event.notify(ObjectCreatedEvent(current_object[objname]))



class ZipExport(object):
    """Export plugin that compresses a folder object into a zip file
    """
    implements(IExport)
    adapts(IExportable)

    def __init__(self, context):
        self.context = context
        self.zipfile = None

    def do_export(self, filename, obj=None, path=None):
        """We recurse in the folder object and export each subobject"""
        if obj is None:
            # first call
            obj = self.context
            path = ''
            self.zipfile = zipfile.ZipFile(filename, 'w')
        else:
            # we are recursing
            if IFile.providedBy(obj):
                self.zipfile.write(obj._data._current_filename(),
                                   path.encode('utf-8'))
        if IContainer.providedBy(obj) or obj is self.context:
            for o in obj:
                self.do_export(filename, obj=obj[o], path=path + '/' + o)
        if obj is self.context:
            # if we are at the end and at the highest level, we're done
            self.zipfile.close()



