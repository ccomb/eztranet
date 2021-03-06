import unittest

import zope

from zope.testing import doctest, doctestunit
from zope.app.testing.setup import placefulSetUp, placefulTearDown
from zope.file.file import File
from zope.app.folder import rootFolder

from eztranet.comment.testing import commentSetUp


def buildTestFile() :
    """ Returns a file that is located in a site. """
    root = rootFolder()
    root[u"file.txt"] = File()
    return root[u"file.txt"]


def setUpBrowserTests(test) :

    placefulSetUp()
    commentSetUp()


def tearDownBrowserTests(test) :

    placefulTearDown()



def test_suite():
    optionflags = doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS
    globs = {'pprint': doctestunit.pprint,
             'TestRequest': zope.publisher.browser.TestRequest}

    return unittest.TestSuite((
        doctest.DocTestSuite("eztranet.comment.browser.comment",
                                setUp=setUpBrowserTests,
                                tearDown=tearDownBrowserTests,
                                optionflags=optionflags
                             ),

        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
