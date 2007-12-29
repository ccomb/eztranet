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

$Id: comments.py 69006 2006-07-06 15:31:31Z oestermeier $
"""

from persistent import Persistent
from persistent.dict import PersistentDict

from zope.component import adapts
from zope.event import notify
from zope.interface import implements

from zope.annotation.interfaces import IAnnotations
from zope.app.file import File
from zope.lifecycleevent import Attributes, Sequence
from zope.lifecycleevent import ObjectCreatedEvent, ObjectModifiedEvent
from zope.location import Location

from eztranet.comment import IAnnotatableComments
from eztranet.comment import IComment
from eztranet.comment import IComments
from eztranet.comment import ICommentSequence

commentsKey = 'comment.comments'

class CommentSequence(Sequence) :
    """Special modification description that distinguishes between
       sequence additions or modifications.
       
       XXX This distinction should probably go into
       
       zope.lifecycleevent.Sequence
       
       later on.
    """
    
    implements(ICommentSequence)
    
    changes = "add", "edit", "del"

    def __init__(self, key, change) :
        self.interface = IComments
        self.keys = (key,)
        self.change = change
        

def dottedName(klass):
    if klass is None:
        return 'None'
    return klass.__module__ + '.' + klass.__name__



class Comment(File):
    """Comment implementation."""

    implements(IComment)



class Comments(Location, Persistent):
    """Comments that will be annotated to an object."""

    implements(IComments)

    __nextKey__ = 0
    
    def __init__(self):
        self.comments = PersistentDict()

    # private methods
    def _get_nextKey(self):
        key = self.__nextKey__
        self.__nextKey__ = nextKey = key + 1
        return nextKey 

    _nextKey = property(_get_nextKey)

    # public methods
    def __getitem__(self, key):
        """See zope.interface.common.mapping.IItemMapping"""
        return self.comments.__getitem__(key)

    def get(self, key, default=None):
        """See zope.interface.common.mapping.IReadMapping"""
        return self.comments.get(key, default)

    def __contains__(self, key):
        """See zope.interface.common.mapping.IReadMapping"""
        return self.comments.__contains__(key)

    def keys(self):
        """See zope.interface.common.mapping.IEnumerableMapping"""
        return self.comments.keys()

    def __iter__(self):
        """See zope.interface.common.mapping.IEnumerableMapping"""
        return self.comments.__iter__()

    def values(self):
        """See zope.interface.common.mapping.IEnumerableMapping"""
        return self.comments.values()

    def items(self):
        """See zope.interface.common.mapping.IEnumerableMapping"""
        return self.comments.items()

    def __len__(self):
        """See zope.interface.common.mapping.IEnumerableMapping"""
        return self.comments.__len__()

    def addComment(self, data, contentType='text/plain'):
        """See comment.IAddComments"""
        comment = Comment(data, contentType)
        key = self._nextKey
        # add dc modification data
        notify(ObjectCreatedEvent(comment))

        self.comments[key] = comment
        return key

    def editComment(self, key, data, contentType='text/plain'):
        """See comment.IEditComments"""
        comment = self.comments[key]

        changed = ()
        if comment.data != data:
            comment.data = data
            changed = changed + ('data',)

        if comment.contentType != contentType:
            comment.contentType = contentType
            changed = changed + ('contentType',)

        if changed:
            notify(ObjectModifiedEvent(comment, Attributes(IComment, *changed)))
        
        return changed
         

    def __delitem__(self, key):
        """See comment.IDeleteComments"""
        del self.comments[key]



class CommentsForAnnotatableComments(Location):
    """Annotate comments."""

    adapts(IAnnotatableComments,)
    implements(IComments)

    def __init__(self, context):
        self.context = context

    # private methods
    def _get_comments(self):
        annotations = self.__dict__.get('_annotations')
        
        if annotations is None:
            self.__dict__['_annotations']= annotations = IAnnotations(self.context)
        
        return annotations.get(commentsKey, None)

    comments = property(_get_comments)

    def _assert_comments(self):
        if self._get_comments() is None:
            self.__dict__['_annotations'][commentsKey] = Comments()

    # public methods
    def __getitem__(self, key):
        """See zope.interface.common.mapping.IItemMapping"""
        if self.comments is not None:
            return self.comments.__getitem__(key)
        else:
            raise KeyError(key)

    def get(self, key, default=None):
        """See zope.interface.common.mapping.IReadMapping"""
        if self.comments is not None:
            return self.comments.get(key, default)
        else:
            return default

    def __contains__(self, key):
        """See zope.interface.common.mapping.IReadMapping"""
        if self.comments is not None:
            return self.comments.__contains__(key)
        else:
            return False

    def keys(self):
        """See zope.interface.common.mapping.IEnumerableMapping"""
        if self.comments is not None:
            return self.comments.keys()
        else:
            return []

    def __iter__(self):
        """See zope.interface.common.mapping.IEnumerableMapping"""
        if self.comments is not None:
            return self.comments.__iter__()
        else:
            return iter([])

    def values(self):
        """See zope.interface.common.mapping.IEnumerableMapping"""
        if self.comments is not None:
            return self.comments.values()
        else:
            return []

    def items(self):
        """See zope.interface.common.mapping.IEnumerableMapping"""
        if self.comments is not None:
            return self.comments.items()
        else:
            return []

    def __len__(self):
        """See zope.interface.common.mapping.IEnumerableMapping"""
        if self.comments is not None:
            return self.comments.__len__()
        else:
            return 0

    def addComment(self, data, contentType='text/plain'):
        """See comment.IAddComments"""
        self._assert_comments()
        key = self.comments.addComment(data, contentType)
        notify(ObjectModifiedEvent(self.context, CommentSequence(key, "add")))
        return key

    def editComment(self, key, data, contentType='text/plain'):
        """See comment.IEditComments"""
        if self.comments is not None:
            changed = self.comments.editComment(key, data, contentType)
            if changed:
                notify(ObjectModifiedEvent(self.context, CommentSequence(key, "edit")))
            return changed
        else:
            raise KeyError(key)

    def __delitem__(self, key):
        """See comment.IDeleteComments"""
        if self.comments is not None:
            self.comments.__delitem__(key)
            notify(ObjectModifiedEvent(self.context, CommentSequence(key, "del")))
        else:
            raise KeyError(key)
