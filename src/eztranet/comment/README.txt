========
Comments
========

This package can be used to comment components. The provided functionality relies
on the annotations mechanism. We implement a subject that we are going to
comment afterward:

    >>> from zope.app.container.contained import Contained
    >>> from zope.interface import implements
    >>> from eztranet.comment import IAttributeAnnotatableComments

    >>> class Subject(Contained):
    ...     implements(IAttributeAnnotatableComments)
    ...     pass

    >>> subject = Subject()

The comment annotated comments can be retrieved by an adaption to IComments:

    >>> from eztranet.comment import IComments

    >>> comments = IComments(subject)

The comments can be read using the regular IEnumerableMapping.
At the moment no comments are stored within comments:

    >>> comments['xy']
    Traceback (most recent call last):
    ...
    KeyError: 'xy'

    >>> comments.get('xy')

    >>> 'xy' in comments
    False

    >>> comments.keys()
    []

    >>> [i for i in comments]
    []

    >>> comments.values()
    []

    >>> comments.items()
    []

    >>> len(comments)
    0

You can add comments. If no content type is defined `text/plain` is
assumed as default. The method `addComment` returns the `key` of the
justly added comment. The addition notifies serveral object events
for the adapted context and the added comment:

    >>> comments.addComment('foo')
    1

    >>> from zope.component.eventtesting import events, clearEvents
    >>> len(events)
    3

    >>> e = events.pop()
    >>> (e.object == subject, e.__class__.__name__ , 
    ...  e.descriptions[0].interface.__name__, e.descriptions[0].keys)
    (True, 'ObjectModifiedEvent', 'IComments', (1,))

    >>> e = events.pop()
    >>> e.object == comments[1], e.__class__.__name__ 
    (True, 'ObjectCreatedEvent')

We add a few more comments...:

    >>> comments.addComment('<bar />', 'text/xml')
    2
    >>> comments.addComment('<html />', 'text/html')
    3

... and check the read methods:

    >>> comments[1] # doctest: +ELLIPSIS
    <eztranet.comment.comments.Comment...>

    >>> comments.get(1) # doctest: +ELLIPSIS
    <eztranet.comment.comments.Comment...>

    >>> 1 in comments
    True

    >>> pprint(comments.keys())
    [1, 2, 3]

    >>> pprint([i for i in comments])
    [1, 2, 3]

    >>> pprint([(v.data, v.contentType) for v in comments.values()]) # doctest: +ELLIPSIS
    [('foo',
      'text/plain'),
     ('<bar />',
      'text/xml'),
     ('<html />',
      'text/html')]

    >>> pprint(comments.items()) # doctest: +ELLIPSIS
    [(1,
      <eztranet.comment.comments.Comment...>),
     (2,
      <eztranet.comment.comments.Comment...>),
     (3,
      <eztranet.comment.comments.Comment...>)]

    >>> len(comments)
    3

You can iterate over the comments:

    >>> for comment in comments.values():
    ...     print comment.data, comment.contentType
    foo text/plain
    <bar /> text/xml
    <html /> text/html

You can delete comment passing its key. The deletion notifies
an object modified event for the context:

    >>> clearEvents()

    >>> del comments[2]
    >>> len(comments)
    2
    
    >>> comments.keys()
    [1, 3]
    
    >>> len(events)
    1

    >>> e = events.pop()
    >>> (e.object == subject, e.__class__.__name__ , 
    ...  e.descriptions[0].interface.__name__, e.descriptions[0].change)
    (True, 'ObjectModifiedEvent', 'IComments', 'del')

You can edit a comment passing its key, its data and optionaly its contentType.
An edition notifies an object modified event for the context and a object
modified event for the comment itself. The events are only fired if there
are obvious changes. Those changes are returned by the `editComment` method
too:

    >>> comments.editComment(3, '<html />', 'text/html')
    ()
    >>> len(events)
    0

    >>> comments.editComment(3, '<html></html>', 'text/html')
    ('data',)
    >>> len(events)
    2

    >>> e = events.pop()
    >>> (e.object == subject, e.__class__.__name__ , 
    ...  e.descriptions[0].interface.__name__, e.descriptions[0].keys)
    (True, 'ObjectModifiedEvent', 'IComments', (3,))

    >>> e = events.pop()
    >>> (e.object == comments[3], e.__class__.__name__ , 
    ...  e.descriptions[0].interface.__name__, e.descriptions[0].attributes)
    (True, 'ObjectModifiedEvent', 'IComment', ('data',))
