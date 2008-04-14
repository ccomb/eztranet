import unittest
from zope.testing import doctest, doctestunit
from zope.app import zapi
from zope.app.testing import ztapi
from zope.app.testing.setup import placefulSetUp, placefulTearDown

def setUp(test):
    site = placefulSetUp(True)


def tearDown(test):
    placefulTearDown()

def test_suite( ):
    return unittest.TestSuite((
        doctest.DocFileSuite('project/project.txt', 
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
