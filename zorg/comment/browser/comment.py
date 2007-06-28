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

$Id: comment.py 38895 2005-10-07 15:09:36Z dominikhuber $
"""
__docformat__ = 'restructuredtext'

import zope

from zope.interface import implements
from zope.component import adapts
from zope.dublincore.interfaces import IZopeDublinCore
from zope.app import zapi
from zope.publisher.browser import TestRequest
from zope.publisher.browser import BrowserView
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.security.interfaces import PrincipalLookupError

from zorg.comment import IComments


def getFullName(principal_id) :
    """ Returns the full name or title of a principal that can be used
        for better display.
        
        Returns the id if the full name cannot be found.
    """
    try :
        return zapi.principals().getPrincipal(principal_id).title
    except (PrincipalLookupError, AttributeError) :
        return principal_id
        

class ListComments(BrowserView) :
    """ A simple list view for comments.
    
    >>> from zorg.comment.browser.tests import buildTestFile
    >>> file = buildTestFile()
    
    
    >>> AddComment(file, TestRequest()).addComment("A comment")
    >>> AddComment(file, TestRequest()).addComment("Another comment")
    
    >>> comments = ListComments(file, TestRequest())
    >>> print comments.render()
    <div id="comments"><a name="comment1"></a>
    ...
    <div>A comment</div>
    ...
    <a name="comment2"></a>
    ...
    <div>Another comment</div>
    ...
    
   
    
    """

    _comment = ViewPageTemplateFile("./templates/comment.pt")
        
    def __init__(self, context, request) :
        super(ListComments, self).__init__(context, request)
        self.comments = IComments(self.context)
        
    def render(self) :
    
        result = ['<div id="comments">']
        
        comments = self.comments
        for key, value in comments.items() :
            info = self.info = dict()
            dc = IZopeDublinCore(value)
            info['key'] = key
            info['who'] = ", ".join(getFullName(x) for x in dc.creators)
            info['when'] = dc.created
            info['text'] = unicode(value.data, encoding="utf-8")
            
            result.append(self._comment())
        
        result.append('</div>')
        
        return "".join(result)
        
        
class AddComment(BrowserView) :
    """ A simple add view for comments. Allows the user to type comments
        and submit them.
        
    """
        
    def nextURL(self) :
        url = zapi.absoluteURL(self.context, self.request)
        return url + "/@@comments.html"
        
    def addComment(self, text) :
        comments = IComments(self.context)
        comments.addComment(text)
        
        self.request.response.redirect(self.nextURL())
        
    
    
    
    
