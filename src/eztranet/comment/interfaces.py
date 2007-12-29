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

$Id: interfaces.py 69006 2006-07-06 15:31:31Z oestermeier $
"""

from zope.interface import Interface, Attribute
from zope.interface.common.mapping import IEnumerableMapping
from zope.annotation.interfaces import IAnnotatable
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.lifecycleevent.interfaces import ISequence
from zope.app.file.interfaces import IFile




class IComment(IFile):
    """Comment."""



class IReadComments(IEnumerableMapping):
    """Read a comments of a comment collection."""



class IAnnotatableComments(IAnnotatable):
    """This interface marks components that should provide annotatable comments.
    
    Components has to provide a annotations mechanismu."""



class IAttributeAnnotatableComments(IAnnotatableComments, IAttributeAnnotatable):
    """This interface marks components that should provide attribute annotatable comments."""



class IDeleteComments(Interface):
    """Remove a comment from the comment collection."""

    def __delitem__(key):
        """x.__delitem__(key) <==> del x[key]
        
        Declaring this interface does not specify whether __delitem__
        supports slice objects."""



class IAddComments(Interface):
    """Add a comment to the comment collection."""

    def addComment(data, contentType='text/plain'):
        """Create a new comment and add it to the comment collection.

        Return the key of the added comment.
        """



class IEditComments(Interface):
    """Edit a comment of the comment collection."""

    def editComment(key, data, contentType='text/plain'):
        """Edit a comment.

        Change only modified parameters.
        Return a tuple of the changed attributes.
        """



class IComments(IReadComments, IAddComments, IEditComments, IDeleteComments):
    """A collection of comments."""



class ICommentSequence(ISequence) :
    """A modification descriptor for a sequence of comments."""
    
    change = Attribute("Allowed change descriptions are 'add', 'edit', 'del'.")