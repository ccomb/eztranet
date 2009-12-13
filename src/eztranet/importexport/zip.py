import zipfile, os
from zope.interface import implements
from zope.component import createObject, adapts
from interfaces import IImportable, IImport
from interfaces import IExportable, IExport

class ZipImport(object):
    """Import plugin that uncompress a zipfile into file and folder objects
    """
    implements(IImport)
    adapts(IImportable)

    def __init__(self, context):
        self.context = context

    def do_import(self, filename):
        zfile = zipfile.ZipFile(filename)
        for f in zfile.infolist():
            # we recreate the hierarchy to the object
            current_object = self.context
            for d in f.filename.split(os.path.sep)[:-1]:
                if d is '': continue
                if d not in current_object:
                    current_object[d] = createObject('eztranet.importexport.container')
                current_object = current_object[d]
            objname = f.filename.split(os.path.sep)[-1]
            if objname not in current_object:
                current_object[objname] = createObject('eztranet.importexport.file')
                # we assume the created object is a file-like object
                newfile = current_object[objname].open('w')
                newfile.write(zfile.read(f.filename))
                newfile.close()



class ZipExport(object):
    """Export plugin that compresses a folder object into a zip file
    """
    implements(IExport)
    adapts(IExportable)

    def __init__(self, context):
        self.context = context

    def do_export(self, filename):
        raise NotImplementedError



