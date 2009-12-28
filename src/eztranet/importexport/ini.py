import logging
from zope.interface import implements, providedBy
from zope.component import adapts
from interfaces import IExport, IImport, IExportable, IImportable
from ConfigParser import ConfigParser

logger = logging.getLogger(__name__)

class IniExport(object):
    """serialize an object in INI file format,
    according to its interfaces

    This is currently only for test purposes
    """
    implements(IExport)
    adapts(IExportable)

    def __init__(self, context):
        self.context = context

    def do_export(self, filename):
        config = ConfigParser()
        fd = open(filename, 'w')

        # export attributes
        interfaces = providedBy(self.context)
        for i in interfaces:
            config.add_section(i.__name__)
            attributes = i.names()
            for a in attributes:
                # don't export methods
                if hasattr(getattr(self.context, a), '__call__'):
                    continue
                #TODO: export the attribute with an adapter on the schema
                config.set(i.__name__,
                           a,
                           getattr(self.context, a).encode('utf-8'))
        config.write(fd)
        fd.close()


class IniImport(object):
    """deserialize an object from an INI file

    This is currently only for test purposes
    """
    implements(IImport)
    adapts(IImportable)

    def __init__(self, context):
        self.context = context

    def do_import(self, filename):
        config = ConfigParser()
        config.read(filename)

        # import attributes for each interface
        interface_names = [i.__name__ for i in providedBy(self.context)]
        sections = config.sections()
        for s in sections:
            if s not in interface_names:
                logger.warn(
                  u"Not restoring attributes from %s as %s instance does'nt provide it"
                  % (s, self.context.__class__))
                continue
            options = config.options(s)
            for o in options:
                value = config.get(s, o)
                setattr(self.context, o, value.decode('utf-8'))

