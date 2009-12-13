from zope.interface import Interface


class IExport(Interface):
    """Interface offered by exportable objects or adapters
    """
    def do_export(filename):
        """Export the object to filename
        """


class IImport(Interface):
    """Interface offered by importable objects or adapters
    """
    def do_import(filename):
        """Import the object from filename
        """


class IExportable(Interface):
    """Marker interface for exportable objects
    """


class IImportable(Interface):
    """Marker interface for importable objects
    """
