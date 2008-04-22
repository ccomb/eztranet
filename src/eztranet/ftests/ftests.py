import unittest
import os.path
from zope.testing import doctest
from zope.app.testing.functional import FunctionalDocFileSuite, ZCMLLayer
from zope.file.testing import FunctionalBlobDocFileSuite

ftesting_zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')

def test_suite( ):
    suite = FunctionalBlobDocFileSuite('eztranet.txt')
    suite.layer = ZCMLLayer(ftesting_zcml, __name__, 'FunctionalLayer')

    return unittest.TestSuite((suite,))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
