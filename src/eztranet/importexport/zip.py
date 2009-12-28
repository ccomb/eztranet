import zipfile, os
from zope.interface import implements
from zope.component import createObject, adapts, getUtility, IFactory
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
                    current_object[d].__name__ = d
                current_object = current_object[d]
            objname = f.filename.split(os.path.sep)[-1]
            if objname not in current_object:
                current_object[objname] = createObject('eztranet.importexport.file')
                current_object[objname].__name__ = objname
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
        # get the types that correspond to the file and folders
        self.folder_type = getUtility(IFactory, name='eztranet.importexport.container')
        self.file_type = getUtility(IFactory, name='eztranet.importexport.file')
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
            if isinstance(obj, self.file_type):
                #FIXME: here we assume the obj is a zope.file blob
                self.zipfile.write(obj._data._current_filename(),
                                   path.encode('utf-8'))
        if isinstance(obj, self.folder_type) or obj is self.context:
            for o in obj:
                self.do_export(filename, obj=obj[o], path=path + '/' + o)
        if obj is self.context:
            # if we are at the end and at the highest level, we're done
            self.zipfile.close()



