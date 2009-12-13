import unittest
from zope.testing import doctest, doctestunit

def setUp(test):
    pass

def tearDown(test):
    pass

def test_suite( ):
    return unittest.TestSuite((
        doctest.DocFileSuite('importexport.txt',
                             setUp=setUp,
                             tearDown=tearDown,
                             globs={'pprint': doctestunit.pprint},
                             optionflags=doctest.NORMALIZE_WHITESPACE+
                                         doctest.ELLIPSIS
                             ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
