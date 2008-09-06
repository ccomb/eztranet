import unittest
from zope.testing import doctest, doctestunit
from zope.app import zapi
from zope.app.testing import ztapi
from zope.app.testing.setup import placefulSetUp, placefulTearDown

def setUp(test):
    site = placefulSetUp(True)

    # zope.annotations
    from zope.annotation.interfaces import IAnnotations
    from zope.annotation.interfaces import IAttributeAnnotatable
    from zope.annotation.attribute import AttributeAnnotations
    from zope.component import provideAdapter
    from eztranet.config.interfaces import IConfigurable, IConfig
    from eztranet.config.config import Config
    provideAdapter(AttributeAnnotations, [IAttributeAnnotatable], IAnnotations)
    ztapi.provideAdapter(IConfigurable, IConfig, Config)


def tearDown(test):
    placefulTearDown()

def test_suite( ):
    return unittest.TestSuite((
        doctest.DocFileSuite('thumbnail.txt', 
                             setUp=setUp, 
                             tearDown=tearDown,
                             globs={'zapi': zapi,
                                    'ztapi': ztapi,
                                    'pprint': doctestunit.pprint},
                             optionflags=doctest.NORMALIZE_WHITESPACE+
                                         doctest.ELLIPSIS
                             ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
