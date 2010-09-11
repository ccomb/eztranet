import unittest
from zope.testing import doctest, doctestunit
from zope.app.testing.setup import placefulSetUp, placefulTearDown
from zope.component import getGlobalSiteManager

def setUp(test):
    site = placefulSetUp(True)
    # register the Config adapter for tests
    from config import Config
    getGlobalSiteManager().registerAdapter(Config)


def tearDown(test):
    placefulTearDown()

def test_suite( ):
    return unittest.TestSuite((
        doctest.DocFileSuite('config.txt',
                             setUp=setUp,
                             tearDown=tearDown,
                             globs={'pprint': doctestunit.pprint},
                             optionflags=doctest.NORMALIZE_WHITESPACE+
                                         doctest.ELLIPSIS
                             ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
