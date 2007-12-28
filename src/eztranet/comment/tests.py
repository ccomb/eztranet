##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id: tests.py 39651 2005-10-26 18:36:17Z oestermeier $
"""

import unittest

from zope.testing import doctest, doctestunit

from zope.app import zapi
from zope.app.testing import ztapi

from zorg.comment.testing import placelesssetup
  


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt', 
                                setUp=placelesssetup.setUp, 
                                tearDown=placelesssetup.tearDown,
                                globs={'zapi': zapi, 'ztapi': ztapi,
                                    'pprint': doctestunit.pprint},
                                optionflags=doctest.NORMALIZE_WHITESPACE+
                                            doctest.ELLIPSIS
                             ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
