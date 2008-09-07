import unittest
import os.path
from zope.app.testing.functional import ZCMLLayer
from zope.file.testing import FunctionalBlobDocFileSuite

ftesting_zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')

def test_suite( ):
    suite = [FunctionalBlobDocFileSuite('eztranet.txt'),
             FunctionalBlobDocFileSuite('thumbnailconfig.txt'),
            ]
    for s in suite:
        s.layer = ZCMLLayer(ftesting_zcml, __name__, 'FunctionalLayer')

    return unittest.TestSuite(suite)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
