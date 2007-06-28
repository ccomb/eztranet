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

$Id: testing.py 69006 2006-07-06 15:31:31Z oestermeier $
"""

import zope.component

import zope.app.testing.placelesssetup

def commentSetUp(test=None) :
    
    # zope.annotations
    from zope.annotation.interfaces import IAnnotations
    from zope.annotation.interfaces import IAnnotatable
    from zope.annotation.interfaces import IAttributeAnnotatable
    from zope.annotation.attribute import AttributeAnnotations

    zope.component.provideAdapter(AttributeAnnotations,
        [IAttributeAnnotatable], IAnnotations)

    # comment.comments adapter
    from zorg.comment.comments import CommentsForAnnotableComments
    from zorg.comment import IComments
    zope.component.provideAdapter(CommentsForAnnotableComments, provides=IComments)
    
    # make DublinCore work
    
    from zope.app.file import File
    from zorg.comment.comments import Comment
    from zorg.comment.interfaces import IAttributeAnnotableComments
    
    from zope.dublincore.interfaces import IZopeDublinCore
    from zope.dublincore.annotatableadapter import ZDCAnnotatableAdapter


    zope.interface.classImplements(File, IAnnotatable)
    zope.interface.classImplements(File, IAttributeAnnotatable)
    zope.interface.classImplements(File, IAttributeAnnotableComments)
    
    zope.interface.classImplements(Comment, IAnnotatable)
    zope.interface.classImplements(Comment, IAttributeAnnotatable)
    
    zope.component.provideAdapter(ZDCAnnotatableAdapter,
                                            [IAnnotatable], 
                                            IZopeDublinCore)
        

class PlacelessSetup(zope.app.testing.placelesssetup.PlacelessSetup):

    def setUp(self, doctesttest=None):
        super(PlacelessSetup, self).setUp(doctesttest)
        commentSetUp(doctesttest)
        

    def tearDown(self, test=None):
        super(PlacelessSetup, self).tearDown()

placelesssetup = PlacelessSetup()


