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

from eztranet.comment import IComments, IAnnotatableComments
from eztranet.eztranet import EztranetSimpleMenuItem
from z3c.layer.pagelet import IPageletBrowserLayer
#from z3c.menu.simple.menu import SimpleMenuItem
from z3c.pagelet.browser import BrowserPagelet
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.security.interfaces import PrincipalLookupError
from zope.authentication.interfaces import IAuthentication
from zope.component import adapts, getUtility
from zope.contentprovider.interfaces import IContentProvider
from zope.dublincore.interfaces import IZopeDublinCore
from zope.i18nmessageid import MessageFactory
from zope.interface import implements, Interface
from zope.publisher.browser import BrowserView
from zope.security.checker import canAccess
from zope.security.interfaces import ForbiddenAttribute
from zope.traversing.browser import absoluteURL

_ = MessageFactory('eztranet')

def getFullName(principal_id) :
    """ Returns the full name or title of a principal that can be used
        for better display.

        Returns the id if the full name cannot be found.
    """
    try :
        return getUtility(IAuthentication).getPrincipal(principal_id).id
    except (PrincipalLookupError, AttributeError) :
        return principal_id


class ListComments(BrowserPagelet) :
    """ A simple list view for comments.

    >>> from eztranet.comment.browser.tests import buildTestFile
    >>> file = buildTestFile()

    >>> from zope.publisher.browser import TestRequest
    >>> AddComment(file, TestRequest()).addComment("A comment")
    >>> AddComment(file, TestRequest()).addComment("Another comment")

    >>> comments = ListComments(file, TestRequest())
    >>> print comments.render_comments()
    <div id="comments"><a name="comment1">
    ...
    <div class="comment">A comment</div>
    ...
    <a name="comment2">
    ...
    <div class="comment">Another comment</div>
    ...



    """

    _comment = ViewPageTemplateFile("./templates/comment.pt")

    def __init__(self, context, request) :
        super(ListComments, self).__init__(context, request)
        self.comments = IComments(self.context)

    def render_comments(self) :
        delkey = None
        if 'del' in self.request.form: # removal of comments (disabled)
            for key, value in self.comments.items() :
                if str(key) == self.request.form['del']:
                    del self.comments[key]

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
    def removable(self):
        try:
            if canAccess(self.comments, '__delitem__'):
                return True
        except ForbiddenAttribute:
            return False

class ListCommentsMenuItem(EztranetSimpleMenuItem):
    url = 'comments.html'
    title = _(u'Comments')
    icon = '/@@/images/list.png'


class AddComment(BrowserView) :
    """ A simple add view for comments. Allows the user to type comments
        and submit them.

    """

    def nextURL(self) :
        url = absoluteURL(self.context, self.request)
        return url + "/@@comments.html"

    def addComment(self, text) :
        comments = IComments(self.context)
        comments.addComment(text)

        self.request.response.redirect(self.nextURL())

class NbComments(object):
    """
    Content provider that gives the number of comments
    """
    implements(IContentProvider)
    adapts(IAnnotatableComments, IPageletBrowserLayer, Interface)

    def __init__(self, context, request, view):
        self.context, self.request, self.view = context, request, view

    def update(self):
        self.nb_comments = len(IComments(self.context))

    def render(self):
        return self.nb_comments

